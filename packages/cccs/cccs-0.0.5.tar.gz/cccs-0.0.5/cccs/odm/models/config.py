from typing import List, Dict

from cccs import odm
from cccs.common.loader import APP_NAME, APP_PREFIX


@odm.model(index=False, store=False, description="Redis Service configuration")
class RedisServer(odm.Model):
    host: str = odm.Keyword(description="Hostname of Redis instance")
    port: int = odm.Integer(description="Port of Redis instance")


DEFAULT_REDIS_NP = {
    "host": "127.0.0.1",
    "port": 6379
}

DEFAULT_REDIS_P = {
    "host": "127.0.0.1",
    "port": 6380
}


@odm.model(index=False, store=False)
class APMServer(odm.Model):
    server_url: str = odm.Optional(odm.Keyword(), description="URL to API server")
    token: str = odm.Optional(odm.Keyword(), description="Authentication token for server")


DEFAULT_APM_SERVER = {
    'server_url': None,
    'token': None
}


@odm.model(index=False, store=False, description="Metrics Configuration")
class Metrics(odm.Model):
    apm_server: APMServer = odm.Compound(APMServer, default=DEFAULT_APM_SERVER, description="APM server configuration")


DEFAULT_METRICS = {
    'apm_server': DEFAULT_APM_SERVER
}


@odm.model(index=False, store=False, description="Redis Configuration")
class Redis(odm.Model):
    nonpersistent: RedisServer = odm.Compound(RedisServer, default=DEFAULT_REDIS_NP,
                                              description="A volatile Redis instance")
    persistent: RedisServer = odm.Compound(RedisServer, default=DEFAULT_REDIS_P,
                                           description="A persistent Redis instance")


DEFAULT_REDIS = {
    "nonpersistent": DEFAULT_REDIS_NP,
    "persistent": DEFAULT_REDIS_P
}


@odm.model(index=False, store=False, description="Core Component Configuration")
class Core(odm.Model):
    metrics: Metrics = odm.Compound(Metrics, default=DEFAULT_METRICS,
                                    description="Configuration for Metrics Collection")
    redis: Redis = odm.Compound(Redis, default=DEFAULT_REDIS, description="Configuration for Redis instances")


DEFAULT_CORE = {
    "redis": DEFAULT_REDIS,
}


@odm.model(index=False, store=False, description="Parameters associated to ILM Policies")
class ILMParams(odm.Model):
    warm = odm.Integer(description="How long, per unit of time, should a document remain in the 'warm' tier?")
    cold = odm.Integer(description="How long, per unit of time, should a document remain in the 'cold' tier?")
    delete = odm.Integer(description="How long, per unit of time, should a document remain before being deleted?")
    unit = odm.Enum(['d', 'h', 'm'], description="Unit of time used by `warm`, `cold`, `delete` phases")


DEFAULT_ILM_PARAMS = {
    "warm": 5,
    "cold": 15,
    "delete": 30,
    "unit":  "d"
}


@odm.model(index=False, store=False, description="Index Lifecycle Management")
class ILM(odm.Model):
    enabled = odm.Boolean(description="Are we enabling ILM across indices?")
    days_until_archive = odm.Integer(description="Days until documents get archived")
    indexes: Dict[str, ILMParams] = odm.Mapping(odm.Compound(ILMParams), default=DEFAULT_ILM_PARAMS,
                                                description="Index-specific ILM policies")
    update_archive = odm.Boolean(description="Do we want to update documents in the archive?")


DEFAULT_ILM = {
    "days_until_archive": 15,
    "enabled": False,
    "indexes": {},
    "update_archive": False
}


@odm.model(index=False, store=False, description="Datastore Configuration")
class Datastore(odm.Model):
    hosts: List[str] = odm.List(odm.Keyword(), description="List of hosts used for the datastore")
    ilm = odm.Compound(ILM, default=DEFAULT_ILM, description="Index Lifecycle Management Policy")
    type = odm.Enum({"elasticsearch"}, description="Type of application used for the datastore")


DEFAULT_DATASTORE = {
    "hosts": ["http://elastic:devpass@localhost"],
    "ilm": DEFAULT_ILM,
    "type": "elasticsearch",
}


@odm.model(index=False, store=False, description="Filestore Configuration")
class Filestore(odm.Model):
    storage: List[str] = odm.List(odm.Keyword(), description="List of filestores used for storage")


DEFAULT_FILESTORE = {
    "storage": [f"s3://{APP_PREFIX}_storage_key:Ch@ngeTh!sPa33w0rd@"
                f"localhost:9000?s3_bucket={APP_PREFIX}-storage&use_ssl=False"]
}


@odm.model(index=False, store=False, description="Model Definition for the Logging Configuration")
class Logging(odm.Model):
    log_level: str = odm.Enum(values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "DISABLED"],
                              description="What level of logging should we have?")
    log_to_console: bool = odm.Boolean(description="Should we log to console?")
    log_to_file: bool = odm.Boolean(description="Should we log to files on the server?")
    log_directory: str = odm.Keyword(description="If `log_to_file: true`, what is the directory to store logs?")
    log_to_syslog: bool = odm.Boolean(description="Should logs be sent to a syslog server?")
    syslog_host: str = odm.Keyword(description="If `log_to_syslog: true`, provide hostname/IP of the syslog server?")
    syslog_port: int = odm.Integer(description="If `log_to_syslog: true`, provide port of the syslog server?")
    export_interval: int = odm.Integer(description="How often, in seconds, should counters log their values?")
    log_as_json: bool = odm.Boolean(description="Log in JSON format?")


DEFAULT_LOGGING = {
    "log_directory": f"/var/log/{APP_NAME}/",
    "log_as_json": True,
    "log_level": "INFO",
    "log_to_console": True,
    "log_to_file": False,
    "log_to_syslog": False,
    "syslog_host": "localhost",
    "syslog_port": 514,
    "export_interval": 5,
}


@odm.model(index=False, store=False, description="CCCS Deployment Configuration")
class Config(odm.Model):
    core: Core = odm.Compound(Core, default=DEFAULT_CORE, description="Core component configuration")
    datastore: Datastore = odm.Compound(Datastore, default=DEFAULT_DATASTORE, description="Datastore configuration")
    filestore: Filestore = odm.Compound(Filestore, default=DEFAULT_FILESTORE, description="Filestore configuration")
    logging: Logging = odm.Compound(Logging, default=DEFAULT_LOGGING, description="Logging configuration")


DEFAULT_CONFIG = {
    "core": DEFAULT_CORE,
    "datastore": DEFAULT_DATASTORE,
    "filestore": DEFAULT_FILESTORE,
    "logging": DEFAULT_LOGGING,
}


if __name__ == "__main__":
    # When executed, the config model will print the default values of the configuration
    import yaml
    print(yaml.safe_dump(Config(DEFAULT_CONFIG).as_primitives()))
