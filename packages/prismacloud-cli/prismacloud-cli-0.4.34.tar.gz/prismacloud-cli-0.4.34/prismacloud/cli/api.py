""" CLI Configuration and Prisma Cloud API Library Wrapper """

import json
import logging
import os
import types

try:
    from pathlib import Path
    homefolder = str(Path.home())
except Exception as _exc:  # pylint:disable=broad-except
    logging.debug("Searching homefolder with pathlib not working, fallback: %s", _exc)
    if "USERPROFILE" in os.environ:
        homefolder = os.environ["USERPROFILE"]
    else:
        homefolder = os.environ["HOME"]

import click
import prismacloud.api.version as api_version
from prismacloud.api import pc_api

import prismacloud.cli.version as cli_version

""" CLI Configuration """


def map_cli_config_to_api_config():
    """map cli configuration to api configuration"""
    try:
        click.get_current_context()
    except Exception as exc:  # pylint:disable=broad-except
        logging.debug("Error getting current context: %s", exc)
    settings = get_cli_config()
    return {
        "api": settings["api_endpoint"],
        "api_compute": settings["pcc_api_endpoint"],
        "username": settings["access_key_id"],
        "password": settings["secret_key"],
        "ca_bundle": False,
    }


def get_cli_config():
    '''
    Try to access params["configuration"]. If this is equal to
    env or environment, try to read environment variables

    PC_SAAS_API_ENDPOINT
    PC_COMPUTE_API_ENDPOINT
    PC_ACCESS_KEY
    PC_SECRET_KEY

    If not all of these are set, try to read a config file.
    '''

    params = {}
    try:
        params = click.get_current_context().find_root().params
    except Exception as exc:  # pylint:disable=broad-except
        params["configuration"] = "credentials"
        logging.debug("Error getting current context: %s", exc)

    # If params["configuration"] is environment
    # try to read environment variables
    try:
        if params["configuration"] == "environment":
            logging.debug("Using environment variables")
            config = {}
            config["api_endpoint"] = os.environ.get("PC_SAAS_API_ENDPOINT", "")
            config["pcc_api_endpoint"] = os.environ.get("PC_COMPUTE_API_ENDPOINT", "")
            config["access_key_id"] = os.environ.get("PC_ACCESS_KEY", "")
            config["secret_key"] = os.environ.get("PC_SECRET_KEY", "")

            logging.debug("Environment variable found: PC_SAAS_API_ENDPOINT: %s", config["api_endpoint"])
            logging.debug("Environment variable found: PC_COMPUTE_API_ENDPOINT: %s", config["pcc_api_endpoint"])

            # Mask all except the first two characters of PC_ACCESS_KEY and PC_SECRET_KEY
            masked_access_key = config["access_key_id"][:3] + "*" * (len(config["access_key_id"]) - 4)
            masked_secret_key = config["secret_key"][:3] + "*" * (len(config["secret_key"]) - 4)

            logging.debug("Environment variable found: PC_ACCESS_KEY: %s", masked_access_key)
            logging.debug("Environment variable found: PC_SECRET_KEY: %s", masked_secret_key)

            return config
    except Exception as exc:  # pylint:disable=broad-except
        logging.debug("Error getting current context: %s", exc)

    """Read or write cli configuration from or to a file"""

    # To fix calling 'pc' without a command.
    if "configuration" not in params:
        params["configuration"] = "credentials"
    logging.info(
        "Running prismacloud-cli version %s using prismacloud-api version %s", cli_version.version, api_version.version
    )
    config_directory = homefolder + "/.prismacloud/"
    config_file_name = config_directory + params["configuration"] + ".json"
    if not os.path.exists(config_directory):
        logging.info("Configuration directory does not exist, creating $HOME/.prismacloud")
        try:
            os.makedirs(config_directory)
        except Exception as exc:  # pylint:disable=broad-except
            logging.info("An error has occured: %s", exc)
    if os.path.exists(config_directory + params["configuration"] + ".json"):
        try:
            config_file_settings = read_cli_config_file(config_file_name)
        except Exception as exc:  # pylint:disable=broad-except
            logging.info("An error has occured: %s", exc)
        logging.debug("Configuration loaded from file: %s", config_file_name)
    else:
        config_file_settings = {
            "api_endpoint": input("Enter your CSPM API URL (Optional if PCCE), eg: api.prismacloud.io: "),
            "pcc_api_endpoint": input(
                "Enter your CWPP API URL (Optional if PCEE), eg: example.cloud.twistlock.com/tenant or twistlock.example.com: "
            ),
            "access_key_id": input("Enter your Access Key (or Username if PCCE): "),
            "secret_key": input("Enter your Secret Key (or Password if PCCE): "),
        }
        json_string = json.dumps(config_file_settings, sort_keys=True, indent=4)
        with open(config_file_name, "w") as config_file:
            config_file.write(json_string)
            logging.debug("Configuration written to file: %s", config_file_name)
    return config_file_settings


def read_cli_config_file(config_file_name):
    """Read cli configuration from a file"""
    logging.debug("Reading configuration from file: %s", config_file_name)
    try:
        with open(config_file_name, "r") as config_file:
            config_file_settings = json.load(config_file)
    except Exception as exc:  # pylint:disable=broad-except
        logging.info("An error has occured: %s", exc)
    if not ("api_endpoint" in config_file_settings and config_file_settings["api_endpoint"]):
        config_file_settings["api_endpoint"] = ""
    return config_file_settings


""" Prisma Cloud API Library Wrapper """


def get_endpoint(_self, endpoint, query_params=None, api="cwpp", request_type="GET"):
    """Make a request without using an endpoint-specific method"""
    pc_api.configure(map_cli_config_to_api_config())
    logging.debug("Calling API Endpoint (%s): %s", request_type, endpoint)
    result = None
    if api == "cspm":
        result = pc_api.execute(request_type, endpoint, query_params)
    if api == "cwpp":
        if not endpoint.startswith("api"):
            endpoint = "api/v1/%s" % endpoint
        result = pc_api.execute_compute(request_type, endpoint, query_params)
    if api == "code":
        result = pc_api.execute_code_security(request_type, endpoint, query_params)
    return result


""" Instance of the Prisma Cloud API """

pc_api.configure(map_cli_config_to_api_config())
# Add the get_endpoint method to this instance.
pc_api.get_endpoint = types.MethodType(get_endpoint, pc_api)
