from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from . database import get_db


# JWT settings
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def verify_access_token(token: str, credentials_exception):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         id: str = str(payload.get("user_id"))
#         ##id: str = payload.get("user_id")
#         if id is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(id=id)
#     except JWTError:
#         raise credentials_exception
#     return token_data
#########################################################TESTETSTETSTE
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"JWT Payload: {payload}")  # 🔍 Debug line
        
        user_id = payload.get("user_id")
        print(f"user_id from payload: {user_id}")  # 🔍 Debug line
        
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id)
        print(f"TokenData created: {token_data}")  # 🔍 Debug line
    except JWTError as e:
        print(f"JWT Error: {e}")  # 🔍 Debug line
        raise credentials_exception
    return token_data
######################TEST TEST TEST #################################



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    return user

