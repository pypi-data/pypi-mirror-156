"""
Django's standard crypto functions and utilities.
"""
import hashlib
import hmac
import secrets

from django_signer.utils.encoding import force_bytes

class InvalidAlgorithm(ValueError):
    """Algorithm is not supported by hashlib."""

    pass


def salted_hmac(key_salt, value, secret, *, algorithm="sha1"):
    """
    Return the HMAC of 'value', using a key generated from key_salt and a
    secret (which defaults to settings.SECRET_KEY). Default algorithm is SHA1,
    but any algorithm name supported by hashlib can be passed.

    A different key_salt should be passed in for every application of HMAC.
    """

    key_salt = force_bytes(key_salt)
    secret = force_bytes(secret)
    try:
        hasher = getattr(hashlib, algorithm)
    except AttributeError as e:
        raise InvalidAlgorithm(
            "%r is not an algorithm accepted by the hashlib module." % algorithm
        ) from e
    # We need to generate a derived key from our base key.  We can do this by
    # passing the key_salt and our base key through a pseudo-random function.
    key = hasher(key_salt + secret).digest()
    # If len(key_salt + secret) > block size of the hash algorithm, the above
    # line is redundant and could be replaced by key = key_salt + secret, since
    # the hmac module does the same thing for keys longer than the block size.
    # However, we need to ensure that we *always* do this.
    return hmac.new(key, msg=force_bytes(value), digestmod=hasher)


RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def get_random_string(length, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return "".join(secrets.choice(allowed_chars) for i in range(length))


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return secrets.compare_digest(force_bytes(val1), force_bytes(val2))


# # TODO: Remove when dropping support for PY38. inspect.signature() is used to
# # detect whether the usedforsecurity argument is available as this fix may also
# # have been applied by downstream package maintainers to other versions in
# # their repositories.
# if func_supports_parameter(hashlib.md5, "usedforsecurity"):
#     md5 = hashlib.md5
#     new_hash = hashlib.new
# else:

#     def md5(data=b"", *, usedforsecurity=True):
#         return hashlib.md5(data)

#     def new_hash(hash_algorithm, *, usedforsecurity=True):
#         return hashlib.new(hash_algorithm)
