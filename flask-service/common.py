import os
from functools import wraps

import jwt
import mysql.connector
from flask import Request, request
from minio import Minio

MYSQL_HOST = os.environ["MYSQL_HOST"]
CONN = mysql.connector.connect(
    user="root", password="123456", host=MYSQL_HOST, port=3306, database="aws_test"
)
CURSOR = CONN.cursor()
MINIO_HOST = os.environ["MINIO_HOST"]
MINIO_CLIENT = Minio(
    f"{MINIO_HOST}:9000", access_key="root", secret_key="12345678", secure=False
)

BUCKET_NAME = "task-attachment"
if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_NAME)
SECRET_KEY = "cloud-computing-secret"


def user_verified(request: Request) -> str:
    """Judge whether the request contains correct Token"""
    try:
        token = request.headers["Authorization"]
    except KeyError:
        return "Token not found"
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Token invalid"
    username = decoded["sub"]
    CURSOR.execute(f"SELECT token FROM User WHERE username='{username}'")
    user_token = CURSOR.fetchone()
    if user_token[0] != token:
        return "Token incorrect"
    setattr(request, "username", username)
    return "OK"


def auth(handler):
    """A decorator to judge whether request contains correct Token"""

    @wraps(handler)
    def _wrapped_view(*args, **kwargs):
        verified = user_verified(request)
        if verified != "OK":
            return verified, 500
        return handler(*args, **kwargs)

    return _wrapped_view


def parse_args(request: Request, *args) -> list:
    dic = request.json
    res = []
    for arg in args:
        val = dic.get(arg, None)
        if val is None:
            raise KeyError(f"http parameter {arg} not found")
        res.append(val)
    return res
