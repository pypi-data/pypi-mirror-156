from .get_salt import get_salt
from .get_hashed_password import get_hashed_password
from .get_token import get_token

def get_token_with_raw_password(
    api_url: str,
    password: str,
    timeout: float = 3.0,
) -> str:
    salt = get_salt(api_url=api_url)
    hashed_password = get_hashed_password(password=password, salt=salt)

    token = get_token(
        api_url=api_url,
        hashed_password=hashed_password,
        timeout=timeout
    )

    return token
