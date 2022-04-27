import json
from typing import NamedTuple

from nacl.exceptions import CryptoError
from nacl.signing import SigningKey as NaClSigningKey
from nacl.signing import VerifyKey

from .misc import bytes_to_hex, hex_to_bytes


class KeyPair(NamedTuple):
    public: str
    private: str


def generate_signature(signing_key: str, message: bytes) -> str:
    return NaClSigningKey(hex_to_bytes(signing_key)).sign(message).signature.hex()


def normalize_dict(dict_: dict) -> bytes:
    return json.dumps(dict_, separators=(',', ':'), sort_keys=True).encode('utf-8')


def is_signature_valid(verify_key: str, message: bytes, signature: str) -> bool:
    try:
        verify_key_bytes = hex_to_bytes(verify_key)
        signature_bytes = hex_to_bytes(signature)
    except ValueError:
        return False

    try:
        VerifyKey(verify_key_bytes).verify(message, signature_bytes)
    except CryptoError:
        return False

    return True


def generate_key_pair() -> KeyPair:
    signing_key = NaClSigningKey.generate()
    return KeyPair(bytes_to_hex(signing_key.verify_key), bytes_to_hex(bytes(signing_key)))


def is_dict_signature_valid(dict_: dict) -> bool:
    dict_ = dict_.copy()
    if not (sender := dict_.get('sender')) or not (signature := dict_.pop('signature', None)):
        return False

    message = normalize_dict(dict_)
    return is_signature_valid(sender, message, signature)


def sign_dict(signing_key: str, dict_: dict):
    assert 'signature' not in dict_
    dict_['signature'] = generate_signature(signing_key, normalize_dict(dict_))