"""
These schemas define the configuration of event settings.
Each event contains an ABI (which is converted to a list
  by using `json.loads(abi)` over the original string
  value and using that result in the spec itself - it
  will be converted to string later when needed to be
  used as argument), a contract address (a valid, but
  not checksum-verified, hexadecimal address), and the
  handler that will be used to process each event in the
  list of events of a given block.
"""


EVENT = {
    "address": {
        "type": "string",
        "required": True,
        "regex": "0x[a-fA-F0-9]{40}"
    },
    "abi": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "allow_unknown": True,
            "schema": {
                "name": {
                    "dependencies": {"type": ["function", "fallback", "receive", "event"]},
                    "type": "string",
                    "regex": "[a-zA-Z][a-zA-Z0-9_]+"
                },
                "type": {
                    "type": "string",
                    "allowed": ["constructor", "function", "fallback", "receive", "event"]
                },
            }
        }
    },
    "event": {
        "type": "string",
        "required": True,
        "regex": "[a-zA-Z][a-zA-Z0-9_]+"
    },
    "handler": {
        "type": "event-handler",
        "required": True
    }
}


EVENTS_SETTINGS = {
    "type": "dict",
    "empty": False,
    "keysrules": {
        "type": "string",
        "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
    },
    "valuesrules": {
        "type": "dict",
        "schema": EVENT
    }
}


# This schema is meant for the worker loop. It will be
# validated with the WorkerSettingsValidator class.
WORKER_SCHEMA = {
    "events": EVENTS_SETTINGS,
    "gateway_url_environment_var": {
        "type": "string",
        "required": True,
        "regex": r"[a-zA-Z_][a-zA-Z0-9_]+",  # The url itself will satisfy: r"https?://[\w_-]+(\.[\w_-]+)*(:\d+)/?"
        "default": "GATEWAY_URL"
    }
}
