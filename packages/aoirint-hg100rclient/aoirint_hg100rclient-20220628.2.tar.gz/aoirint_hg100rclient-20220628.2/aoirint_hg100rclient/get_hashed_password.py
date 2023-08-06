import hashlib

def get_hashed_password(
    password: str,
    salt: str,
) -> str:
    dk = hashlib.pbkdf2_hmac(
        hash_name='sha1',
        password=password.encode('ascii'),
        salt=salt.encode('ascii'),
        iterations=2048,
        dklen=16,
    )

    return dk.hex()
