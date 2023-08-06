from abc import ABC, abstractmethod
from functools import wraps, cached_property
from datetime import datetime, timezone, timedelta
from copy import deepcopy
import base64
import hashlib
import uuid
import weakref
from resotolib.logger import log
from enum import Enum
from typing import Dict, Iterator, List, ClassVar, Optional
from resotolib.utils import make_valid_timestamp, ResourceChanges
from prometheus_client import Counter, Summary
from dataclasses import dataclass, field


metrics_resource_pre_cleanup_exceptions = Counter(
    "resource_pre_cleanup_exceptions_total",
    "Number of resource pre_cleanup() exceptions",
    ["cloud", "account", "region", "kind"],
)
metrics_resource_cleanup_exceptions = Counter(
    "resource_cleanup_exceptions_total",
    "Number of resource cleanup() exceptions",
    ["cloud", "account", "region", "kind"],
)
metrics_resource_cleanup = Summary("resoto_resource_cleanup_seconds", "Time it took the resource cleanup() method")


def unless_protected(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not isinstance(self, BaseResource):
            raise ValueError("unless_protected() only supports BaseResource type objects")
        if self.protected:
            log.error(f"Resource {self.rtdname} is protected - refusing modification")
            self.log(("Modification was requested even though resource is protected" " - refusing"))
            return False
        return f(self, *args, **kwargs)

    return wrapper


class EdgeType(Enum):
    default = "default"
    delete = "delete"

    @staticmethod
    def from_value(value: Optional[str] = None) -> Enum:
        try:
            return EdgeType(value)
        except ValueError:
            pass
        return EdgeType.default


@dataclass(eq=False)
class BaseResource(ABC):
    """A BaseResource is any node we're connecting to the Graph()

    BaseResources have an id, name and tags. The id is a unique id used to search for
    the resource within the Graph. The name is used for display purposes. Tags are
    key/value pairs that get exported in the GRAPHML view.

    There's also class variables, kind, phantom and successor_kinds.
    `kind` is a string describing the type of resource, e.g. 'aws_ec2_instance'
       or 'some_cloud_load_balancer'.
    `phantom` is a bool describing whether the resource actually exists within
       the cloud or if it's just a phantom resource like pricing information
       or usage quota. I.e. some information relevant to the cloud account
       but not actually existing in the form of a usable resource.
    `successor_kinds` is a list of kinds that can be connected to this resource for
       the related edge type.
    """

    kind: ClassVar[str] = "resource"
    phantom: ClassVar[bool] = False
    successor_kinds: ClassVar[Dict[str, List[str]]] = {"default": [], "delete": []}

    id: str
    tags: Dict[str, Optional[str]] = None
    name: str = None
    _cloud: object = field(default=None, repr=False)
    _account: "BaseAccount" = field(default=None, repr=False)
    _region: object = field(default=None, repr=False)
    _zone: object = field(default=None, repr=False)
    _resotocore_id: Optional[str] = field(default=None, repr=False)
    _resotocore_revision: Optional[str] = field(default=None, repr=False)
    _resotocore_query_tag: Optional[str] = field(default=None, repr=False)
    ctime: Optional[datetime] = field(
        default=None,
        metadata={"synthetic": {"age": "trafo.duration_to_datetime"}},
    )
    mtime: Optional[datetime] = field(
        default=None,
        metadata={"synthetic": {"last_update": "trafo.duration_to_datetime"}},
    )
    atime: Optional[datetime] = field(
        default=None,
        metadata={"synthetic": {"last_access": "trafo.duration_to_datetime"}},
    )

    def __post_init__(self) -> None:
        if self.name is None:
            self.name = self.id
        self.uuid = uuid.uuid4().hex
        self._clean: bool = False
        self._cleaned: bool = False
        self._protected: bool = False
        self._changes: ResourceChanges = ResourceChanges(self)
        self._deferred_connections: List = []
        self.__graph = None
        self.__log: List = []
        self._raise_tags_exceptions: bool = False
        self.max_graph_depth: int = 0
        if not hasattr(self, "_tags"):
            self._tags = None
        if not hasattr(self, "_ctime"):
            self._ctime = None
        if not hasattr(self, "_atime"):
            self._atime = None
        if not hasattr(self, "_mtime"):
            self._mtime = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}('{self.id}', name='{self.name}',"
            f" region='{self.region().name}', zone='{self.zone().name}',"
            f" account='{self.account().dname}', kind='{self.kind}',"
            f" ctime={self.ctime!r}, uuid={self.uuid}, chksum={self.chksum})"
        )

    def _keys(self) -> tuple:
        """Return a tuple of all keys that make this resource unique

        Must not be called before the resource is connected to the graph
        as the relative location within the graph is used to determine the
        tuple of unique keys.

        E.g. instance -> aws -> 123457 -> us-east-1 -> us-east-1b -> i-987654 -> myServer
        """
        if self._graph is None:
            raise RuntimeError(f"_keys() called on {self.rtdname} before resource was added to graph")
        return (
            self.kind,
            self.cloud().id,
            self.account().id,
            self.region().id,
            self.zone().id,
            self.id,
            self.name,
        )

    #    def __hash__(self):
    #        return hash(self._keys())

    #    def __eq__(self, other):
    #        if isinstance(other, type(self)):
    #            return self._keys() == other._keys()
    #        return NotImplemented

    @property
    def dname(self) -> str:
        if self.id == self.name:
            return self.id
        return f"{self.name} ({self.id})"

    @property
    def kdname(self) -> str:
        return f"{self.kind} {self.dname}"

    rtdname = kdname

    def _tags_getter(self) -> Dict:
        return self._tags

    def _tags_setter(self, value: Dict) -> None:
        if value is None:
            value = {}
        self._tags = ResourceTagsDict(dict(value), parent_resource=self)

    def log(self, msg: str, data=None, exception=None) -> None:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        log_entry = {
            "timestamp": now,
            "msg": str(msg),
            "exception": repr(exception) if exception else None,
            "data": deepcopy(data),
        }
        self.__log.append(log_entry)
        self._changes.add("log")

    @property
    def resource_type(self) -> str:
        return self.kind

    @property
    def changes(self) -> ResourceChanges:
        return self._changes

    @property
    def event_log(self) -> List:
        return self.__log

    @property
    def str_event_log(self) -> List:
        return [
            {
                "timestamp": le["timestamp"].isoformat(),
                "msg": le["msg"],
                "exception": le["exception"],
            }
            for le in self.__log
        ]

    def update_tag(self, key, value) -> bool:
        raise NotImplementedError

    def delete_tag(self, key) -> bool:
        raise NotImplementedError

    @cached_property
    def chksum(self) -> str:
        """Return a checksum of the resource."""
        return (
            base64.urlsafe_b64encode(hashlib.blake2b(str(self._keys()).encode(), digest_size=16).digest())
            .decode("utf-8")
            .rstrip("=")
        )

    @property
    def age(self) -> Optional[timedelta]:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if self.ctime is not None:
            return now - self.ctime

    @property
    def last_access(self) -> Optional[timedelta]:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if self.atime is not None:
            return now - self.atime

    @property
    def last_update(self) -> Optional[timedelta]:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if self.mtime is not None:
            return now - self.mtime

    def _ctime_getter(self) -> Optional[datetime]:
        if "resoto:ctime" in self.tags:
            ctime = self.tags["resoto:ctime"]
            try:
                ctime = make_valid_timestamp(datetime.fromisoformat(ctime))
            except ValueError:
                pass
            else:
                return ctime
        return self._ctime

    def _ctime_setter(self, value: Optional[datetime]) -> None:
        self._ctime = make_valid_timestamp(value)

    def _atime_getter(self) -> Optional[datetime]:
        return self._atime

    def _atime_setter(self, value: Optional[datetime]) -> None:
        self._atime = make_valid_timestamp(value)

    def _mtime_getter(self) -> Optional[datetime]:
        return self._mtime

    def _mtime_setter(self, value: Optional[datetime]) -> None:
        self._mtime = make_valid_timestamp(value)

    @property
    def clean(self) -> bool:
        return self._clean

    @clean.setter
    @unless_protected
    def clean(self, value: bool) -> None:
        if self.phantom and value:
            raise ValueError(f"Can't cleanup phantom resource {self.rtdname}")

        clean_str = "" if value else "not "
        self.log(f"Setting to {clean_str}be cleaned")
        log.debug(f"Setting {self.rtdname} to {clean_str}be cleaned")
        self._changes.add("clean")
        self._clean = value

    @property
    def cleaned(self) -> bool:
        return self._cleaned

    @property
    def protected(self) -> bool:
        return self._protected

    @protected.setter
    def protected(self, value: bool) -> None:
        """Protects the resource from cleanup
        This property acts like a fuse, once protected it can't be unprotected
        """
        if self.protected:
            log.debug(f"Resource {self.rtdname} is already protected")
            return
        if value:
            log.debug(f"Protecting resource {self.rtdname}")
            self.log("Protecting resource")
            self._changes.add("protected")
            self._protected = value

    @metrics_resource_cleanup.time()
    @unless_protected
    def cleanup(self, graph=None) -> bool:
        if self.phantom:
            raise RuntimeError(f"Can't cleanup phantom resource {self.rtdname}")

        if self.cleaned:
            log.debug(f"Resource {self.rtdname} has already been cleaned up")
            return True

        self._changes.add("cleaned")
        if graph is None:
            graph = self._graph

        account = self.account(graph)
        region = self.region(graph)
        if not isinstance(account, BaseAccount) or not isinstance(region, BaseRegion):
            log.error(f"Could not determine account or region for cleanup of {self.rtdname}")
            return False

        log_suffix = f" in account {account.dname} region {region.name}"
        self.log("Trying to clean up")
        log.debug(f"Trying to clean up {self.rtdname}{log_suffix}")
        try:
            if not self.delete(graph):
                self.log("Failed to clean up")
                log.error(f"Failed to clean up {self.rtdname}{log_suffix}")
                return False
            self._cleaned = True
            self.log("Successfully cleaned up")
            log.info(f"Successfully cleaned up {self.rtdname}{log_suffix}")
        except Exception as e:
            self.log("An error occurred during clean up", exception=e)
            log.exception(f"An error occurred during clean up {self.rtdname}{log_suffix}")
            cloud = self.cloud(graph)
            metrics_resource_cleanup_exceptions.labels(
                cloud=cloud.name,
                account=account.dname,
                region=region.name,
                kind=self.kind,
            ).inc()
            return False
        return True

    @unless_protected
    def pre_cleanup(self, graph=None) -> bool:
        if not hasattr(self, "pre_delete"):
            return True

        if graph is None:
            graph = self._graph

        if self.phantom:
            raise RuntimeError(f"Can't cleanup phantom resource {self.rtdname}")

        if self.cleaned:
            log.debug(f"Resource {self.rtdname} has already been cleaned up")
            return True

        account = self.account(graph)
        region = self.region(graph)
        if not isinstance(account, BaseAccount) or not isinstance(region, BaseRegion):
            log.error(("Could not determine account or region for pre cleanup of" f" {self.rtdname}"))
            return False

        log_suffix = f" in account {account.dname} region {region.name}"
        self.log("Trying to run pre clean up")
        log.debug(f"Trying to run pre clean up {self.rtdname}{log_suffix}")
        try:
            if not getattr(self, "pre_delete")(graph):
                self.log("Failed to run pre clean up")
                log.error(f"Failed to run pre clean up {self.rtdname}{log_suffix}")
                return False
            self.log("Successfully ran pre clean up")
            log.info(f"Successfully ran pre clean up {self.rtdname}{log_suffix}")
        except Exception as e:
            self.log("An error occurred during pre clean up", exception=e)
            log.exception(f"An error occurred during pre clean up {self.rtdname}{log_suffix}")
            cloud = self.cloud(graph)
            metrics_resource_pre_cleanup_exceptions.labels(
                cloud=cloud.name,
                account=account.dname,
                region=region.name,
                kind=self.kind,
            ).inc()
            return False
        return True

    @unless_protected
    @abstractmethod
    def delete(self, graph) -> bool:
        raise NotImplementedError

    def account(self, graph=None) -> "BaseAccount":
        account = None
        if graph is None:
            graph = self._graph
        if self._account:
            account = self._account
        elif graph:
            account = graph.search_first_parent_class(self, BaseAccount)
        if account is None:
            account = UnknownAccount("undefined", {})
        return account

    def cloud(self, graph=None) -> "BaseCloud":
        cloud = None
        if graph is None:
            graph = self._graph
        if self._cloud:
            cloud = self._cloud
        elif graph:
            cloud = graph.search_first_parent_class(self, BaseCloud)
        if cloud is None:
            cloud = UnknownCloud("undefined", {})
        return cloud

    def region(self, graph=None) -> "BaseRegion":
        region = None
        if graph is None:
            graph = self._graph
        if self._region:
            region = self._region
        elif graph:
            region = graph.search_first_parent_class(self, BaseRegion)
        if region is None:
            region = UnknownRegion("undefined", {})
        return region

    def zone(self, graph=None) -> "BaseZone":
        zone = None
        if graph is None:
            graph = self._graph
        if self._zone:
            zone = self._zone
        elif graph:
            zone = graph.search_first_parent_class(self, BaseZone)
        if zone is None:
            zone = UnknownZone("undefined", {})
        return zone

    def location(self, graph=None):
        if graph is None:
            graph = self._graph
        zone = self.zone(graph)
        if zone.name != "undefined":
            return zone
        region = self.region(graph)
        if region.name != "undefined":
            return region
        account = self.account(graph)
        if account.name != "undefined":
            return account
        cloud = self.cloud(graph)
        if cloud.name != "undefined":
            return cloud
        return UnknownLocation("undefined", {})

    def add_deferred_connection(
        self, search: Dict, parent: bool = True, edge_type: EdgeType = EdgeType.default
    ) -> None:
        self._deferred_connections.append({"search": search, "parent": parent, "edge_type": edge_type})

    def resolve_deferred_connections(self, graph) -> None:
        if graph is None:
            graph = self._graph
        while self._deferred_connections:
            dc = self._deferred_connections.pop(0)
            node = graph.search_first_all(dc["search"])
            edge_type = dc["edge_type"]
            if node:
                if dc["parent"]:
                    src = node
                    dst = self
                else:
                    src = self
                    dst = node
                graph.add_edge(src, dst, edge_type=edge_type)

    def predecessors(self, graph, edge_type=None) -> Iterator:
        """Returns an iterator of the node's parent nodes"""
        if graph is None:
            graph = self._graph
        if graph is None:
            return ()
        return graph.predecessors(self, edge_type=edge_type)

    def successors(self, graph, edge_type=None) -> Iterator:
        """Returns an iterator of the node's child nodes"""
        if graph is None:
            graph = self._graph
        if graph is None:
            return ()
        return graph.successors(self, edge_type=edge_type)

    def predecessor_added(self, resource, graph) -> None:
        """Called when a predecessor is added to this node"""
        pass

    def successor_added(self, resource, graph) -> None:
        """Called when a successor is added to this node"""
        pass

    def ancestors(self, graph, edge_type=None) -> Iterator:
        """Returns an iterator of the node's ancestors"""
        if graph is None:
            graph = self._graph
        if graph is None:
            return ()
        return graph.ancestors(self, edge_type=edge_type)

    def descendants(self, graph, edge_type=None) -> Iterator:
        """Returns an iterator of the node's descendants"""
        if graph is None:
            graph = self._graph
        if graph is None:
            return ()
        return graph.descendants(self, edge_type=edge_type)

    @property
    def _graph(self):
        if self.__graph is not None:
            return self.__graph()

    @_graph.setter
    def _graph(self, value) -> None:
        self.__graph = weakref.ref(value)

    def __getstate__(self):
        ret = self.__dict__.copy()
        ret["_BaseResource__graph"] = None
        return ret

    def __setstate__(self, state):
        self.__dict__.update(state)


BaseResource.tags = property(BaseResource._tags_getter, BaseResource._tags_setter)
BaseResource.ctime = property(BaseResource._ctime_getter, BaseResource._ctime_setter)
BaseResource.mtime = property(BaseResource._mtime_getter, BaseResource._mtime_setter)
BaseResource.atime = property(BaseResource._atime_getter, BaseResource._atime_setter)


class ResourceTagsDict(dict):
    def __init__(self, *args, parent_resource=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__parent_resource = None
        self.parent_resource = parent_resource

    @property
    def parent_resource(self):
        return self.__parent_resource

    @parent_resource.setter
    def parent_resource(self, value):
        self.__parent_resource = value

    def __setitem__(self, key, value):
        if self.parent_resource and isinstance(self.parent_resource, BaseResource):
            log.debug(f"Calling parent resource to set tag {key} to {value} in cloud")
            try:
                if self.parent_resource.update_tag(key, value):
                    log_msg = f"Successfully set tag {key} to {value} in cloud"
                    self.parent_resource._changes.add("tags")
                    self.parent_resource.log(log_msg)
                    log.info((f"{log_msg} for {self.parent_resource.kind}" f" {self.parent_resource.id}"))
                    return super().__setitem__(key, value)
                else:
                    log_msg = f"Error setting tag {key} to {value} in cloud"
                    self.parent_resource.log(log_msg)
                    log.error((f"{log_msg} for {self.parent_resource.kind}" f" {self.parent_resource.id}"))
            except Exception as e:
                log_msg = f"Unhandled exception while trying to set tag {key} to {value}" f" in cloud: {type(e)} {e}"
                self.parent_resource.log(log_msg, exception=e)
                if self.parent_resource._raise_tags_exceptions:
                    raise
                else:
                    log.exception(log_msg)
        else:
            return super().__setitem__(key, value)

    def __delitem__(self, key):
        if self.parent_resource and isinstance(self.parent_resource, BaseResource):
            log.debug(f"Calling parent resource to delete tag {key} in cloud")
            try:
                if self.parent_resource.delete_tag(key):
                    log_msg = f"Successfully deleted tag {key} in cloud"
                    self.parent_resource._changes.add("tags")
                    self.parent_resource.log(log_msg)
                    log.info((f"{log_msg} for {self.parent_resource.kind}" f" {self.parent_resource.id}"))
                    return super().__delitem__(key)
                else:
                    log_msg = f"Error deleting tag {key} in cloud"
                    self.parent_resource.log(log_msg)
                    log.error((f"{log_msg} for {self.parent_resource.kind}" f" {self.parent_resource.id}"))
            except Exception as e:
                log_msg = f"Unhandled exception while trying to delete tag {key} in cloud:" f" {type(e)} {e}"
                self.parent_resource.log(log_msg, exception=e)
                if self.parent_resource._raise_tags_exceptions:
                    raise
                else:
                    log.exception(log_msg)
        else:
            return super().__delitem__(key)

    def __reduce__(self):
        return super().__reduce__()


@dataclass(eq=False)
class PhantomBaseResource(BaseResource):
    kind: ClassVar[str] = "phantom_resource"
    phantom: ClassVar[bool] = True

    def cleanup(self, graph=None) -> bool:
        log.error(f"Resource {self.rtdname} is a phantom resource and can't be cleaned up")
        return False


@dataclass(eq=False)
class BaseQuota(PhantomBaseResource):
    kind: ClassVar[str] = "quota"
    quota: Optional[float] = None
    usage: Optional[float] = None
    quota_type: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.quota is not None:
            self.quota = float(self.quota)
        if self.usage is not None:
            self.usage = float(self.usage)

    @property
    def usage_percentage(self) -> float:
        if self.quota is not None and self.usage is not None and self.quota > 0.0:
            return self.usage / self.quota * 100
        else:
            return 0.0


@dataclass(eq=False)
class BaseType(BaseQuota):
    kind: ClassVar[str] = "type"


@dataclass(eq=False)
class BaseInstanceQuota(BaseQuota):
    kind: ClassVar[str] = "instance_quota"
    instance_type: Optional[str] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.instance_type = self.id
        self.quota_type = "standard"


@dataclass(eq=False)
class BaseInstanceType(BaseType):
    kind: ClassVar[str] = "instance_type"
    instance_type: Optional[str] = None
    instance_cores: float = 0.0
    instance_memory: float = 0.0
    ondemand_cost: Optional[float] = None
    reservations: Optional[int] = None

    def __post_init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__post_init__()
        if self.instance_type is None:
            self.instance_type = self.id
        if self.reservations is not None:
            self.reservations = int(self.reservations)
        if self.ondemand_cost is not None:
            self.ondemand_cost = float(self.ondemand_cost)


@dataclass(eq=False)
class BaseCloud(BaseResource):
    kind: ClassVar[str] = "base_cloud"

    def cloud(self, graph=None):
        return self


@dataclass(eq=False)
class BaseAccount(BaseResource):
    kind: ClassVar[str] = "account"

    def account(self, graph=None):
        return self


@dataclass(eq=False)
class BaseRegion(BaseResource):
    kind: ClassVar[str] = "region"

    def region(self, graph=None):
        return self


@dataclass(eq=False)
class BaseZone(BaseResource):
    kind: ClassVar[str] = "zone"

    def zone(self, graph=None):
        return self


class InstanceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    BUSY = "busy"
    UNKNOWN = "unknown"


@dataclass(eq=False)
class BaseInstance(BaseResource):
    kind: ClassVar[str] = "instance"
    instance_cores: float = 0.0
    instance_memory: float = 0.0
    instance_type: Optional[str] = ""
    instance_status: Optional[str] = ""

    def instance_type_info(self, graph) -> BaseInstanceType:
        return graph.search_first_parent_class(self, BaseInstanceType)

    def _instance_status_getter(self) -> str:
        return self._instance_status.value

    @abstractmethod
    def _instance_status_setter(self, value: str) -> None:
        raise NotImplementedError


BaseInstance.instance_status = property(BaseInstance._instance_status_getter, BaseInstance._instance_status_setter)


@dataclass(eq=False)
class BaseVolumeType(BaseType):
    kind: ClassVar[str] = "volume_type"
    volume_type: str = ""
    ondemand_cost: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        self.volume_type = self.id


class VolumeStatus(Enum):
    IN_USE = "in-use"
    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    DELETED = "deleted"
    UNKNOWN = "unknown"


@dataclass(eq=False)
class BaseVolume(BaseResource):
    kind: ClassVar[str] = "volume"
    volume_size: int = 0
    volume_type: str = ""
    volume_status: str = ""
    volume_iops: Optional[int] = None
    volume_throughput: Optional[int] = None
    volume_encrypted: Optional[bool] = None
    snapshot_before_delete: bool = False

    def _volume_status_getter(self) -> str:
        return self._volume_status.value

    @abstractmethod
    def _volume_status_setter(self, value: str) -> None:
        raise NotImplementedError

    def volume_type_info(self, graph) -> BaseVolumeType:
        return graph.search_first_parent_class(self, BaseVolumeType)


BaseVolume.volume_status = property(BaseVolume._volume_status_getter, BaseVolume._volume_status_setter)


@dataclass(eq=False)
class BaseSnapshot(BaseResource):
    kind: ClassVar[str] = "snapshot"
    snapshot_status: str = ""
    description: str = ""
    volume_id: Optional[str] = None
    volume_size: int = 0
    encrypted: bool = False
    owner_id: Optional[str] = None
    owner_alias: str = ""


@dataclass(eq=False)
class Cloud(BaseCloud):
    kind: ClassVar[str] = "cloud"

    def delete(self, graph) -> bool:
        return False


@dataclass(eq=False)
class GraphRoot(PhantomBaseResource):
    kind: ClassVar[str] = "graph_root"

    def delete(self, graph) -> bool:
        return False


@dataclass(eq=False)
class BaseBucket(BaseResource):
    kind: ClassVar[str] = "bucket"


@dataclass(eq=False)
class BaseKeyPair(BaseResource):
    kind: ClassVar[str] = "keypair"
    fingerprint: str = ""


@dataclass(eq=False)
class BaseBucketQuota(BaseQuota):
    kind: ClassVar[str] = "bucket_quota"


@dataclass(eq=False)
class BaseNetwork(BaseResource):
    kind: ClassVar[str] = "network"


@dataclass(eq=False)
class BaseNetworkQuota(BaseQuota):
    kind: ClassVar[str] = "network_quota"


@dataclass(eq=False)
class BaseDatabase(BaseResource):
    kind: ClassVar[str] = "database"
    db_type: str = ""
    db_status: str = ""
    db_endpoint: str = ""
    db_version: Optional[str] = None
    db_publicly_accessible: Optional[bool] = None
    instance_type: str = ""
    volume_size: int = 0
    volume_iops: Optional[int] = None
    volume_encrypted: Optional[bool] = None


@dataclass(eq=False)
class BaseLoadBalancer(BaseResource):
    kind: ClassVar[str] = "load_balancer"
    lb_type: str = ""
    public_ip_address: Optional[str] = None
    backends: List[str] = field(default_factory=list)


@dataclass(eq=False)
class BaseLoadBalancerQuota(BaseQuota):
    kind: ClassVar[str] = "load_balancer_quota"


@dataclass(eq=False)
class BaseSubnet(BaseResource):
    kind: ClassVar[str] = "subnet"


@dataclass(eq=False)
class BaseGateway(BaseResource):
    kind: ClassVar[str] = "gateway"


@dataclass(eq=False)
class BaseTunnel(BaseResource):
    kind: ClassVar[str] = "tunnel"


@dataclass(eq=False)
class BaseGatewayQuota(BaseQuota):
    kind: ClassVar[str] = "gateway_quota"


@dataclass(eq=False)
class BaseSecurityGroup(BaseResource):
    kind: ClassVar[str] = "security_group"


@dataclass(eq=False)
class BaseRoutingTable(BaseResource):
    kind: ClassVar[str] = "routing_table"


@dataclass(eq=False)
class BaseNetworkAcl(BaseResource):
    kind: ClassVar[str] = "network_acl"


@dataclass(eq=False)
class BasePeeringConnection(BaseResource):
    kind: ClassVar[str] = "peering_connection"


@dataclass(eq=False)
class BaseEndpoint(BaseResource):
    kind: ClassVar[str] = "endpoint"


@dataclass(eq=False)
class BaseNetworkInterface(BaseResource):
    kind: ClassVar[str] = "network_interface"
    network_interface_status: str = ""
    network_interface_type: str = ""
    mac: str = ""
    private_ips: List[str] = field(default_factory=list)
    public_ips: List[str] = field(default_factory=list)
    v6_ips: List[str] = field(default_factory=list)
    description: str = ""


@dataclass(eq=False)
class BaseUser(BaseResource):
    kind: ClassVar[str] = "user"


@dataclass(eq=False)
class BaseGroup(BaseResource):
    kind: ClassVar[str] = "group"


@dataclass(eq=False)
class BasePolicy(BaseResource):
    kind: ClassVar[str] = "policy"


@dataclass(eq=False)
class BaseRole(BaseResource):
    kind: ClassVar[str] = "role"


@dataclass(eq=False)
class BaseInstanceProfile(BaseResource):
    kind: ClassVar[str] = "instance_profile"


@dataclass(eq=False)
class BaseAccessKey(BaseResource):
    kind: ClassVar[str] = "access_key"
    access_key_status: str = ""


@dataclass(eq=False)
class BaseCertificate(BaseResource):
    kind: ClassVar[str] = "certificate"
    expires: Optional[datetime] = None
    dns_names: Optional[List[str]] = None
    sha1_fingerprint: Optional[str] = None


@dataclass(eq=False)
class BaseCertificateQuota(BaseQuota):
    kind: ClassVar[str] = "certificate_quota"


@dataclass(eq=False)
class BaseStack(BaseResource):
    kind: ClassVar[str] = "stack"
    stack_status: str = ""
    stack_status_reason: str = ""
    stack_parameters: Dict = field(default_factory=dict)


@dataclass(eq=False)
class BaseAutoScalingGroup(BaseResource):
    kind: ClassVar[str] = "autoscaling_group"
    min_size: int = -1
    max_size: int = -1


@dataclass(eq=False)
class BaseIPAddress(BaseResource):
    kind: ClassVar[str] = "ip_address"
    ip_address: str = ""
    ip_address_family: str = ""


@dataclass(eq=False)
class BaseHealthCheck(BaseResource):
    kind: ClassVar[str] = "health_check"
    check_interval: int = -1
    healthy_threshold: int = -1
    unhealthy_threshold: int = -1
    timeout: int = -1
    health_check_type: str = ""


@dataclass(eq=False)
class BaseDNSZone(BaseResource):
    kind: ClassVar[str] = "dns_zone"


@dataclass(eq=False)
class BaseDNSRecordSet(BaseResource):
    kind: ClassVar[str] = "dns_record_set"

    record_ttl: int = -1
    record_type: str = ""
    record_values: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.record_type = self.record_type.upper()

    def _keys(self) -> tuple:
        if self._graph is None:
            raise RuntimeError(f"_keys() called on {self.rtdname} before resource was added to graph")
        return (
            self.kind,
            self.cloud().id,
            self.account().id,
            self.region().id,
            self.zone().id,
            self.id,
            self.name,
            self.record_type,
        )


@dataclass(eq=False)
class BaseDNSRecord(BaseResource):
    kind: ClassVar[str] = "dns_record"

    record_ttl: int = -1
    record_type: str = ""
    record_data: str = ""
    record_value: str = ""
    record_priority: Optional[int] = None
    record_port: Optional[int] = None
    record_weight: Optional[int] = None
    record_flags: Optional[int] = None
    record_tag: Optional[str] = None
    record_mname: Optional[str] = None
    record_rname: Optional[str] = None
    record_serial: Optional[int] = None
    record_refresh: Optional[int] = None
    record_retry: Optional[int] = None
    record_expire: Optional[int] = None
    record_minimum: Optional[int] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.record_type = self.record_type.upper()

    def _keys(self) -> tuple:
        if self._graph is None:
            raise RuntimeError(f"_keys() called on {self.rtdname} before resource was added to graph")
        return (
            self.kind,
            self.cloud().id,
            self.account().id,
            self.region().id,
            self.zone().id,
            self.id,
            self.name,
            self.record_type,
            self.record_data,
        )


@dataclass(eq=False)
class UnknownCloud(BaseCloud):
    kind: ClassVar[str] = "unknown_cloud"

    def delete(self, graph) -> bool:
        return False


@dataclass(eq=False)
class UnknownAccount(BaseAccount):
    kind: ClassVar[str] = "unknown_account"

    def delete(self, graph) -> bool:
        return False


@dataclass(eq=False)
class UnknownRegion(BaseRegion):
    kind: ClassVar[str] = "unknown_region"

    def delete(self, graph) -> bool:
        return False


@dataclass(eq=False)
class UnknownZone(BaseZone):
    kind: ClassVar[str] = "unknown_zone"

    def delete(self, graph) -> bool:
        return False


@dataclass(eq=False)
class UnknownLocation(BaseResource):
    kind: ClassVar[str] = "unknown_location"

    def delete(self, graph) -> bool:
        return False
