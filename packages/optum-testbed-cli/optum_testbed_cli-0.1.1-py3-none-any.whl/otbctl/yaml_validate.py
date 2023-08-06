from schema import Schema, SchemaError, Regex, Or, Optional
import yaml
import re
import logging
import logging.config
from .log_management import log_management

infoLogger = log_management.get_info_logger()
errorLogger = log_management.get_error_logger()

body_regex = r"\{*.\}*."  # anything inside curly braces { }

# stricter requirements can be enacted for any str, using regex or Schema
config_schema = Schema({
    "version": float,
    "workflows": {
        "flow": {
            "source": {
                "auth-endpoint": str,
                # specific error messages are provided to user as such:
                "auth-type": Or("Token", error="auth-type must be 'Token'."),
                "method": Or("POST", "GET", error="method must be 'POST' or 'GET'."),
                "isAuthOnly": Or(bool, error="isAuthOnly must be True or False."),
                "headers": [{object: object}],
                "request": {
                    "api-endpoint": str,
                    "method": Or("POST", "GET", "None"),
                    "auth-type": "Bearer",
                    "token-name": "access_token",
                    "headers": [{object: object}],
                    "params": Or([{object: object}], None),
                    "body": str,
                }
            },
            "testbed": {
                "request": {
                    "method": Or("POST", "GET"),
                    "status": 200,
                    "path": str,
                    "params": Or([{object: object}], None),
                    "headers": [{object: object}],
                    "body":  str,
                }
            }
        }
    }
})

def validate_config(config_yaml):
    with open(config_yaml, 'r') as f:
        file_to_check = yaml.safe_load(f)
    try:
        config_schema.validate(file_to_check)
        infoLogger.info("YAML follows valid pattern")
    except SchemaError as se:
        errorLogger.error("YAML needs changes: ")
        for error in se.errors:
            if error:
                errorLogger.error(error)
        for error in se.autos:
            if error:
                errorLogger.error(error)
        exit()