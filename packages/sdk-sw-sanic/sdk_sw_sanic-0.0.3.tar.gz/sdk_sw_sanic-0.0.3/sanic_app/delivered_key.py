"""here we're creating the Hel Man key exchange"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

parameters = dh.generate_parameters(generator=2, key_size=2048)
server_private_key = parameters.generate_private_key()
peer_private_key = parameters.generate_private_key()


def derived_key():
    """function for sending derived_key"""
    shared_key = server_private_key.exchange(peer_private_key.public_key())
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(shared_key)

    return derived_key


def same_derived_key():
    """function for sending same_derived_key"""
    same_shared_key = peer_private_key.exchange(
        server_private_key.public_key()
    )
    same_derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    ).derive(same_shared_key)

    return same_derived_key


def comparing_key():
    """comparing 2 keys"""
    if derived_key() == same_derived_key():
        print("same")
