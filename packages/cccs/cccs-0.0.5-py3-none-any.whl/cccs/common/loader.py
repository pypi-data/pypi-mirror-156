# This file contains the loaders for the different components of the system
from __future__ import annotations

import os
import yaml

from string import Template
from typing import TYPE_CHECKING

from cccs.common.dict_utils import recursive_update

if TYPE_CHECKING:
    from cccs.odm.models.config import Config

APP_NAME = os.environ.get("APP_NAME", "cccs_common")
APP_PREFIX = os.environ.get("APP_PREFIX", "cccs")

config_cache = {}


def get_classification(yml_config=None):
    from cccs.common.classification import Classification, InvalidDefinition

    if yml_config is None:
        yml_config = f"/etc/{APP_NAME}/classification.yml"

    classification_definition = {}
    default_file = os.path.join(os.path.dirname(__file__), "classification.yml")
    if os.path.exists(default_file):
        with open(default_file) as default_fh:
            default_yml_data = yaml.safe_load(default_fh.read())
            if default_yml_data:
                classification_definition.update(default_yml_data)

    # Load modifiers from the yaml config
    if os.path.exists(yml_config):
        with open(yml_config) as yml_fh:
            yml_data = yaml.safe_load(yml_fh.read())
            if yml_data:
                classification_definition = recursive_update(classification_definition, yml_data)

    if not classification_definition:
        raise InvalidDefinition('Could not find any classification definition to load.')

    return Classification(classification_definition)


def env_substitute(buffer):
    """Replace environment variables in the buffer with their value.

    Use the built in template expansion tool that expands environment variable style strings ${}
    We set the idpattern to none so that $abc doesn't get replaced but ${abc} does.

    Case insensitive.
    Variables that are found in the buffer, but are not defined as environment variables are ignored.
    """
    return Template(buffer).safe_substitute(os.environ, idpattern=None, bracedidpattern='(?a:[_a-z][_a-z0-9]*)')


def _get_config(yml_config=None):
    from cccs.odm.models.config import Config

    if yml_config is None:
        yml_config = f"/etc/{APP_NAME}/config.yml"

    # Initialize a default config
    config = Config().as_primitives()

    # Load modifiers from the yaml config
    if os.path.exists(yml_config):
        with open(yml_config) as yml_fh:
            yml_data = yaml.safe_load(env_substitute(yml_fh.read()))
            if yml_data:
                config = recursive_update(config, yml_data)

    if 'AL_LOG_LEVEL' in os.environ:
        config['logging']['log_level'] = os.environ['AL_LOG_LEVEL']

    return Config(config)


def get_config(yml_config=None) -> Config:
    if yml_config not in config_cache:
        config_cache[yml_config] = _get_config(yml_config=yml_config)
    return config_cache[yml_config]


def get_esstore(config=None, archive_access=False):
    from cccs.datastore.store import ESStore

    if not config:
        config = get_config()

    return ESStore(config=config, archive_access=archive_access)


def get_filestore(config=None, connection_attempts=None):
    from cccs.filestore import FileStore
    if config is None:
        config = get_config()
    return FileStore(*config.filestore.storage, connection_attempts=connection_attempts)
