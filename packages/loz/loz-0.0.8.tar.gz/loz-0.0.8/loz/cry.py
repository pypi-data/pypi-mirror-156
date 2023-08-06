from base64 import b64encode, b64decode, urlsafe_b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
import random
import string

key_size = 4096
msg_size = 446
salt_size = 16


class Pto:
    "cry.Pto see what I did there?"

    def __init__(self, pem, password: str = None):
        if password:
            # pem is private key
            password = password.encode()
            pem = b64decode(pem.encode())
            salt = pem[:salt_size]
            encrypted_pvt = pem[salt_size:]
            fernet_key = Scrypt(salt=salt, length=32, n=2**18, r=8, p=1).derive(
                password
            )
            fernet = Fernet(urlsafe_b64encode(fernet_key))
            pvt = fernet.decrypt(encrypted_pvt)
            self.private_key = serialization.load_pem_private_key(
                data=pvt,
                backend=default_backend(),
                password=None,
            )
            self.public_key = self.private_key.public_key()
            return
        # pem is public key
        self.public_key = serialization.load_pem_public_key(
            data=pem.encode(), backend=default_backend()
        )

    def encrypt(self, message: str):
        bmsg = message.encode()
        ciphertext = bytes()
        for chunk in [bmsg[i : i + msg_size] for i in range(0, len(bmsg), msg_size)]:
            ciphertext += self.public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        return b64encode(ciphertext).decode("utf-8")

    def decrypt(self, ciphertext: str):
        bciph = b64decode(ciphertext.encode())
        message = bytes()
        for chunk in [
            bciph[i : i + key_size // 8] for i in range(0, len(bciph), key_size // 8)
        ]:
            message += self.private_key.decrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        return message.decode("utf-8")


def generate_key_pair(password: str):
    password = password.encode()
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )
    public_key = private_key.public_key()
    pem_pvt = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    salt = os.urandom(salt_size)
    fernet_key = Scrypt(salt=salt, length=32, n=2**18, r=8, p=1).derive(password)
    fernet = Fernet(urlsafe_b64encode(fernet_key))
    encrypted_pvt = fernet.encrypt(pem_pvt)
    serialized_pvt = b64encode(salt + encrypted_pvt).decode("utf-8")
    serialized_pub = pem_pub.decode("utf-8")
    return (serialized_pvt, serialized_pub)


def make_password(length=16):
    selectable_punctuation = "+-=_&?/\\%#@~,."
    chars = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + selectable_punctuation
    )
    password = "".join(random.choice(chars) for x in range(length))
    return password
