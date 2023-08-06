"""
loz functions
"""
from loz import cry, LozException
from os import path
import json
import logging
import secrets

logger = logging.getLogger("loz")


def load(loz_file):
    "Loads .loz file and returns storage object."
    if not path.isfile(loz_file):
        raise LozException(f"no loz file found at {loz_file}")
    storage = None
    logger.debug(f"opening {loz_file}")
    with open(loz_file, "r") as f:
        storage = json.loads(f.read())
        logger.debug(f"loaded storage from {loz_file}")
    return storage


def save(storage, loz_file):
    "Saves storage object as json .loz file."
    logger.debug(f"opening {loz_file}")
    with open(loz_file, "w") as f:
        f.write(json.dumps(storage))
        logger.debug(f"storage written to {loz_file}")


def is_valid_password(storage, password):
    "Tries to unlock storage with a password. Returns True if successful."
    try:
        logger.debug("validating password")
        cry.dec(storage["c"], password)
        return True
    except:
        return False


def init(password):
    "Initialize storage with master password."
    token = secrets.token_bytes(64)
    enc_token = cry.enc(token, password)
    storage = {"c": enc_token, "e": {}}
    return storage


def add(storage, entity, username, secret, password):
    "Set secret for 'entity username' pair."
    encrypted = cry.enc(secret.encode(), password)
    if not entity in storage["e"]:
        logger.debug(f"adding entity {entity} and adding username {username}")
        storage["e"][entity] = {username: encrypted}
    else:
        logger.debug(f"adding username {username} to existing entity {entity}")
        storage["e"][entity][username] = encrypted
    return [entity, username]


def exists(storage, entity, username=None):
    if entity not in storage["e"]:
        return False
    if not username:
        return True
    if username in storage["e"][entity]:
        return True
    return False


def get(storage, entity, username, password):
    "Return secret for 'entity username' pair."
    if entity not in storage["e"] or username not in storage["e"][entity]:
        logger.warning(f"{entity}/{username} does not exist")
        return None
    secret = storage["e"][entity][username]
    return cry.dec(secret, password).decode("utf-8")


def rm(storage, entity, username=None):
    "Delete username from entity or whole entity, return deleted entity/username pair."
    if entity not in storage["e"]:
        return None
    if username and username not in storage["e"][entity]:
        return None
    if username:
        del storage["e"][entity][username]
        if not storage["e"][entity]:
            del storage["e"][entity]
            return [
                entity,
            ]
        return [entity, username]
    else:
        del storage["e"][entity]
        return [
            entity,
        ]


def show(storage, entity, password):
    "List all secrets in one entity."
    secrets = []
    if entity not in storage["e"]:
        return None
    for username in storage["e"][entity]:
        logger.debug("user found, decrypting secret")
        secret = storage["e"][entity][username]
        decrypted = cry.dec(secret, password).decode("utf-8")
        secrets.append([entity, username, decrypted])
    return secrets


def ls(storage, entity=None):
    "List all storage or usernames under one entity."
    if not entity:
        return list(storage["e"].keys())
    if entity not in storage["e"]:
        return []
    return list(storage["e"][entity].keys())


def find(storage, word):
    "List storage and usernames that contain the search phrase."
    results = []
    for entity in storage["e"]:
        if word in entity:
            results.append(
                [
                    entity,
                ]
            )
        for username in storage["e"][entity]:
            if word in username:
                results.append([entity, username])
    return results
