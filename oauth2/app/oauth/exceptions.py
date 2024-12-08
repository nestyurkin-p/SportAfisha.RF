from fastapi import HTTPException, status

CredentialsValidationError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

SessionValidationError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate session",
    headers={"WWW-Authenticate": "Bearer"},
)


class JWTSecretKeyNotFoundError(FileNotFoundError):
    pass
