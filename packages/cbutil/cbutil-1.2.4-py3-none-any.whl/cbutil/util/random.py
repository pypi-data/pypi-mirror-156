import uuid
import base64
import base58

__all__ = [
    'to_uuid_b64url_str',
    'make_uuid4_b64url_str',
    'make_uuid4_b58_str'
]


def to_uuid_b64url_str(uuid):
    return base64.urlsafe_b64encode(uuid.bytes).decode(encoding='utf8')

def to_uuid_b58url_str(uuid):
    return base58.b58encode(uuid.bytes).decode(encoding='utf8')


def make_uuid4_b64url_str():
    return to_uuid_b64url_str(uuid.uuid4())

def make_uuid4_b58_str():
    return to_uuid_b58url_str(uuid.uuid4())



