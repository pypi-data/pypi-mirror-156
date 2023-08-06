def make_evm_erc1155_balance_resource(db_name: str = 'evm', erc1155balance_collection_name: str = 'erc1155-ownership',
                                      erc1155balance_resource_name: str = "evm-erc1155-ownership"):
    """
    Makes an EVM resource to track token ownerships of an ERC-1155 smart contract.
    :return: A dictionary with the resource configuration.
    """

    return {
        erc1155balance_resource_name: {
            "db": db_name,
            "collection": erc1155balance_collection_name,
            "type": "list",
            "verbs": ["list", "read"],
            "schema": {
                "contract-key": {
                    "type": "string",
                    "required": True,
                    "regex": "[a-zA-Z][a-zA-Z0-9-]+"
                },
                "owner": {
                    "type": "string",
                    "required": True,
                    "regex": "0x[a-fA-F0-9]{40}"
                },
                "token": {
                    "type": "string",
                    "required": True,
                    "regex": "0x[a-f0-9]{1,64}"
                },
                "amount": {
                    # This is NOT hex-coded - just stringified.
                    "type": "string",
                    "required": True,
                    "regex": r"\d+"
                }
            },
            "indexes": {
                "lookup": {
                    "unique": True,
                    "fields": ["contract-key", "token", "owner"]
                },
                "owned-list": {
                    "fields": ["contract-key", "owner"]
                }
            }
        }
    }
