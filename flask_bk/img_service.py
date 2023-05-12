import json
import os

import numpy as np
import requests
from PIL import Image

TF_HOST = os.environ["TF_SERVER_HOST"]
TF_SERVICE = (
    f"http://{TF_HOST}:8501/v1/models/efficientnet_v2_imagenet21k_ft1k_s:predict"
)
IMAGENET_CLASSES = "imagenet_class_index.json"


def load_imagenet_labels():
    with open(IMAGENET_CLASSES) as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


class LabelsGetter:
    label_dict = load_imagenet_labels()

    def __call__(self, predictions, topk=5):
        values = list(enumerate(predictions))
        indices = sorted(values, key=lambda x: x[1], reverse=True)[:topk]
        return [self.label_dict[i] for i, _ in indices]


def get_labels(img_data):
    image = Image.open(img_data)
    image = image.resize((384, 384))
    image = image.convert("RGB")
    image = np.expand_dims(np.array(image) / 255.0, 0).tolist()

    response = requests.post(TF_SERVICE, json.dumps({"instances": image}), timeout=2)
    predictions = response.json()["predictions"][0]
    local_getter = LabelsGetter()
    return " ".join(local_getter(predictions, 10))


if __name__ == "__main__":
    ...
