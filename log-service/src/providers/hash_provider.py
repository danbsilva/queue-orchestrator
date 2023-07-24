from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def check_password_hash(password, pwd_hashed) -> bool:
    return pwd_context.verify(password, pwd_hashed)


def generate_password_hash(password) -> str:
    return pwd_context.hash(password)
