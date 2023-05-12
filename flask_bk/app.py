import io
from datetime import datetime, timedelta

import jwt
from flask import Flask, request
from flask_cors import CORS
from minio import Minio
from minio.deleteobjects import DeleteObject

from common import *
from img_service import get_labels

APP = Flask(__name__)
CORS(APP)

MINIO_HOST = os.environ["MINIO_HOST"]
MINIO_CLIENT = Minio(
    f"{MINIO_HOST}:9000", access_key="root", secret_key="12345678", secure=False
)

BUCKET_NAME = "task-attachment"
if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_NAME)


@APP.route("/token", methods=["POST"])
def login():
    username, password = parse_args(request, "username", "password")
    CURSOR.execute(f"SELECT password FROM User WHERE username='{username}'")
    item = CURSOR.fetchone()
    if item is None or password != item[0]:
        return "incorrect auth", 500
    token = jwt.encode(
        {
            "exp": datetime.utcnow() + timedelta(days=1),
            "iat": datetime.utcnow(),
            "sub": username,
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    CURSOR.execute(f"UPDATE User SET token = '{token}' WHERE username = '{username}'")
    CONN.commit()
    return token


@APP.route("/tasks", methods=["POST"])
@auth
def create_task():
    title, body, due_date = parse_args(request, "title", "body", "dueDate")

    CURSOR.execute(
        f"""INSERT INTO Task (title, body, dueDate)
        VALUES ('{title}', '{body}', '{due_date}')"""
    )
    CONN.commit()
    return {"message": "Data inserted successfully"}


@APP.route("/tasks/<int:task_id>", methods=["DELETE"])
@auth
def delete_task(task_id):
    CURSOR.execute(f"SELECT upload FROM Task WHERE id={task_id}")
    upload = CURSOR.fetchone()[0]
    if upload:
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name),
            MINIO_CLIENT.list_objects(
                BUCKET_NAME, f"{request.username}/{task_id}/", recursive=True
            ),
        )
        MINIO_CLIENT.remove_objects(BUCKET_NAME, delete_object_list)
    CURSOR.execute(f"DELETE FROM Task WHERE id={task_id}")
    CONN.commit()
    return {"message": "Task deleted successfully"}


@APP.route("/tasks", methods=["GET"])
@auth
def get_tasks():
    CURSOR.execute("SELECT * FROM Task")
    columns = [col[0] for col in CURSOR.description]
    data = [dict(zip(columns, row)) for row in CURSOR.fetchall()]

    for item in data:
        item["labels"] = item["labels"].split()
    return data


@APP.route("/upload/<int:task_id>", methods=["PUT"])
@auth
def predict_image(task_id):
    img_data = request.stream.read()
    data_len = len(img_data)
    img_data = io.BytesIO(img_data)

    fname = f"{request.username}/{task_id}/{request.headers['X-File-Name']}"
    MINIO_CLIENT.put_object(BUCKET_NAME, fname, img_data, data_len)

    labels = get_labels(img_data)
    CURSOR.execute(f"UPDATE Task SET labels='{labels}', upload=1 WHERE id = {task_id}")
    CONN.commit()
    return {"message": "Label generated successfully"}


if __name__ == "__main__":
    ...
