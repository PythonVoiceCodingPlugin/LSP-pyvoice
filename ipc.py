import base64
import json
import logging
import os
import time
from multiprocessing.connection import Client

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = os.path.expanduser(os.path.join("~", ".voicerpc.json"))


def get_server_path(service):
    if os.name == "nt":
        return r"\\.\pipe\voicerpc\{}\{}".format(
            os.path.split(os.path.expanduser("~"))[-1], service
        )
    else:
        return os.path.expanduser(os.path.join("~/.voicerpc/{}.sock".format(service)))


def get_client(service="default"):
    try:
        with open(CREDENTIALS_FILE) as f:
            credentials = json.load(f)
        encoded_auth = credentials[service]
        auth = base64.b64decode(encoded_auth)
        address = get_server_path(service)
        # print("Pyvoice: connecting to", address)
        conn = Client(address, authkey=auth)

        return conn
    except Exception as e:
        logger.exception("Failed to establish connection")
        return None


def send_notification(method, params, connection=None, log_msg=None):
    start = time.perf_counter()
    connection = connection or get_client()
    if not connection:
        logger.error("No connection. Unable to send notification {}", method)
    msg = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
    }
    client_bytes = json.dumps(msg).encode("utf-8")
    connection.send_bytes(client_bytes)
    end = time.perf_counter()
    logger.info(
        "Notification %s sent %s bytes over %.3f seconds",
        log_msg or method,
        len(client_bytes),
        end - start,
    )
