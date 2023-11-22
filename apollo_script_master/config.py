"""
Here we can create or validate the config file.
In yaml, it looks like:
------------------------------------------------------------------------------------------------------------------------
# ApolloScriptMaster Configuration File

# Global Settings
global:
  dry_run: False  # Set to True for a dry run without actually executing SQL scripts
  isolation_level: READ UNCOMMITTED
  echo: False  # Set to True for SQLAlchemy echo mode (prints SQL statements)

# Checksum Settings
checksum:
  algorithm: sha256  # Set to sha256 or md5
  output_enabled: True  # Set to True to enable checksum verification during script execution
  output_file: checksums.txt  # Checksum output file name

# Deploy Table Settings
deploy_table:
  name: ASMDeploy
  args:
    schema: public

# Deploy Lock Table Settings
deploy_lock_table:
  name: ASMDeployLock
  lock_check_retries: 6
  lock_check_wait: 10  # Time to wait (in seconds) between lock check retries
  args:
    schema: public

# Deploy Deletions Table Settings
deploy_deletions_table:
  name: ASMDeployDeletions
  args:
    schema: public

# Logging Settings
logging:
  log_level: INFO  # Set to INFO, WARNING, ERROR, or CRITICAL for different log levels
  log_file: sql_deploy.log
------------------------------------------------------------------------------------------------------------------------
"""
import logging
import os

import schema
from schema import Optional
import yaml

config_file_schema = schema.Schema(
    {
        "global": {
            "dry_run": bool,
            "isolation_level": str,
            "echo": bool
        },
        "checksum": {
            "algorithm": str,
            "output_enabled": bool,
            "output_file": str
        },
        "deploy_table": {
            "name": str,
            Optional("args"): dict
        },
        "deploy_lock_table": {
            "name": str,
            Optional("args"): dict,
            "lock_check_retries": int,
            "lock_check_wait": int
        },
        "deploy_deletions_table": {
            "name": str,
            Optional("args"): dict
        },
        "logging": {
            "log_level": str,
            "log_file": str
        }
    }
)


def validate_config_file(config_file: str) -> dict:
    """
    Validate the configuration file.
    """
    try:
        with open(config_file, "r") as _rconfig_file:
            config = yaml.safe_load(_rconfig_file)
        config_file_schema.validate(config)
        os.environ["ASP_CONFIG"] = str(config)
        logging.info(f"Configuration file validated at {config_file}.")
        logging.info(f"ASP_CONFIG environment variable set.")
        return config
    except FileNotFoundError as error:
        logging.info(f"An error occurred when trying to read the configuration file: {error}.")
        raise error
    except schema.SchemaError as error:
        logging.info(f"An error occurred when trying to validate the configuration file: {error}.")
        raise error


def generate_config_file(config_file: str) -> None:
    """
    Generate the configuration file.
    """
    config = {
        "global": {
            "dry_run": False,
            "isolation_level": "READ UNCOMMITTED",
            "echo": False
        },
        "checksum": {
            "algorithm": "sha256",
            "output_enabled": True,
            "output_file": "checksums.txt"
        },
        "deploy_table": {
            "name": "ASMDeploy",
            "args": {
                "schema": "public"
            }
        },
        "deploy_lock_table": {
            "name": "ASMDeployLock",
            "lock_check_retries": 6,
            "lock_check_wait": 10,
            "args": {
                "schema": "public"
            }
        },
        "deploy_deletions_table": {
            "name": "ASMDeployDeletions",
            "args": {
                "schema": "public"
            }
        },
        "logging": {
            "log_level": "INFO",
            "log_file": "sql_deploy.log"
        }
    }
    with open(config_file, "w") as _wconfig_file:
        yaml.dump(config, _wconfig_file, default_flow_style=False)
    logging.info(f"Configuration file generated at {config_file}.")
