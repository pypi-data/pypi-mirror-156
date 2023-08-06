"""
loz functions
"""
from loz import cry
from loz.exceptions import *
from os import path
import json
import logging
import secrets

logger = logging.getLogger("loz")

storage_version = "1.0"


def load(loz_file):
    "Loads .loz file and returns storage object."
    if not path.isfile(loz_file):
        raise LozFileDoesNotExist(f"No loz file found at {loz_file}.")
    storage = None
    logger.debug(f"opening {loz_file}")
    with open(loz_file, "r") as f:
        storage = json.loads(f.read())
        logger.debug(f"loaded storage from {loz_file}")
        if storage["version"] > storage_version:
            raise LozIncompatibleFileVersion(
                f"Found lozfile version {storage['version']} but supports up to {storage_version}."
            )
    return storage


def save(storage, loz_file):
    "Saves storage object as json .loz file."
    logger.debug(f"opening {loz_file}")
    storage["version"] = storage_version
    with open(loz_file, "w") as f:
        f.write(json.dumps(storage))
        logger.debug(f"storage written to {loz_file}")


def is_valid_password(storage, password):
    "Tries to unlock storage with a password. Returns True if successful."
    try:
        logger.debug("validating password")
        cry.dec(storage["check"], password)
        return True
    except:
        return False


def init(password):
    "Initialize storage with master password."
    token = secrets.token_bytes(64)
    enc_token = cry.enc(token, password)
    storage = {"check": enc_token, "data": {}}
    return storage


def store(storage, domain, username, secret, password):
    "Store secret for domain/username pair. Return [domain, username, change] list of changed item."
    encrypted = cry.enc(secret.encode(), password)
    if exists(storage, domain, username):  # update existing
        existing_secret = get(storage, domain, username, password)
        if existing_secret == secret:
            logger.debug(f"unchanged secret for {domain}/{username}")
            return []
        logger.debug(f"updating secret for {domain}/{username}")
        storage["data"][domain][username] = encrypted
        return [domain, username, "update secret"]
    if exists(storage, domain):  # add new user
        logger.debug(f"adding username {username} with secret for {domain}")
        storage["data"][domain][username] = encrypted
        return [domain, username, "add username and secret"]
    # add user and domain
    logger.debug(f"adding domain {domain} and username {username} with secret")
    storage["data"][domain] = {username: encrypted}
    return [domain, username, "add domain, username and secret"]


def exists(storage, domain, username=None):
    if domain not in storage["data"]:
        logger.debug(f"domain {domain} does not exist")
        return False
    if not username:
        logger.debug(f"domain {domain} exists")
        return True
    if username in storage["data"][domain]:
        logger.debug(f"username {username} exists in domain {domain}")
        return True
    logger.debug(f"username {username} does not exist in domain {domain}")
    return False


def get(storage, domain, username, password):
    "Return secret for 'domain username' pair."
    if not exists(storage, domain, username):
        logger.warning(f"{domain}/{username} does not exist")
        return None
    secret = storage["data"][domain][username]
    return cry.dec(secret, password).decode("utf-8")


def get_all(storage, password):
    for domain in storage["data"].keys():
        for username in storage["data"][domain].keys():
            yield [
                domain,
                username,
                get(storage, domain, username, password),
            ]


def rm(storage, domain, username=None):
    "Delete username from domain or whole domain, return change."
    if not exists(storage, domain):
        return []
    if username and not exists(storage, domain, username):
        return []
    if username:
        del storage["data"][domain][username]
        if not storage["data"][domain]:
            del storage["data"][domain]
            return [domain, "*", "delete whole domain"]
        return [domain, username, "delete username"]
    else:
        del storage["data"][domain]
        return [domain, "*", "delete whole domain"]


def show(storage, domain, password):
    "List all secrets in one domain."
    secrets = []
    if domain not in storage["data"]:
        return None
    for username in storage["data"][domain]:
        logger.debug("user found, decrypting secret")
        secret = storage["data"][domain][username]
        decrypted = cry.dec(secret, password).decode("utf-8")
        secrets.append([domain, username, decrypted])
    return secrets


def ls(storage, domain=None):
    "List all storage or usernames under one domain."
    if not domain:
        return list(storage["data"].keys())
    if domain not in storage["data"]:
        return []
    return list(storage["data"][domain].keys())


def find(storage, word):
    "List storage and usernames that contain the search phrase."
    results = []
    for domain in storage["data"]:
        if word in domain:
            results.append(
                [
                    domain,
                ]
            )
        for username in storage["data"][domain]:
            if word in username:
                results.append([domain, username])
    return results
