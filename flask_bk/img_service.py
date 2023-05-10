import io
import json

from PIL import Image
import numpy as np
import requests

TF_SERVICE = (
    "http://localhost:8501/v1/models/efficientnet_v2_imagenet21k_ft1k_s:predict"
)
IMAGENET_CLASSES = "imagenet_class_index.json"


def load_imagenet_labels():
    with open(IMAGENET_CLASSES) as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


class LabelsGetter:
    def __init__(self) -> None:
        self.label_dict = load_imagenet_labels()

    def __call__(self, predictions, topk=5):
        values = list(enumerate(predictions))
        indices = sorted(values, key=lambda x: x[1], reverse=True)[:topk]
        return [self.label_dict[i] for i, _ in indices]


LABEL_GETTER = LabelsGetter()


def get_labels(img_data):
    image = Image.open(img_data)
    image = image.resize((384, 384))
    image = image.convert("RGB")
    image = np.expand_dims(np.array(image) / 255.0, 0).tolist()

    response = requests.post(TF_SERVICE, json.dumps({"instances": image}), timeout=2)
    predictions = response.json()["predictions"][0]
    return " ".join(LABEL_GETTER(predictions, 10))


if __name__ == "__main__":
    ...
