from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ApiToken, User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def authenticate_user(
    authorization: str | None = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    """Authenticate incoming request via *Bearer* token.

    Returns the associated ``User`` instance on success or raises HTTP 401/403.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header; expected 'Bearer <token>'",
        )

    token_value = authorization.split(" ", 1)[1].strip()
    api_token: ApiToken | None = db.query(ApiToken).filter(ApiToken.token == token_value, ApiToken.revoked_at == None).first()  # noqa: E712

    if not api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user: User | None = db.query(User).filter(User.id == api_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User associated with token does not exist")

    return user 