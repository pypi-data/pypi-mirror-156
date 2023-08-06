import cv2
import numpy as np
import requests
from random import randint
import os

GENDER_MODEL = "/models/deploy_gender.prototxt"
GENDER_PROTO = "/models/gender_net.caffemodel"
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
GENDER_LIST = ["Male", "Female"]
FACE_PROTO = "/models/deploy.prototxt.txt"
FACE_MODEL = "/models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
AGE_MODEL = "/models/deploy_age.prototxt"
AGE_PROTO = "/models/age_net.caffemodel"
AGE_INTERVALS = [
    "(0, 2)",
    "(4, 6)",
    "(8, 15)",
    "(18, 24)",
    "(27, 33)",
    "(36, 43)",
    "(48, 53)",
    "(60, 100)",
]

path = os.path.abspath(os.path.dirname(__file__))
face_net = cv2.dnn.readNetFromCaffe(path + FACE_PROTO, path + FACE_MODEL)
age_net = cv2.dnn.readNetFromCaffe(path + AGE_MODEL, path + AGE_PROTO)
gender_net = cv2.dnn.readNetFromCaffe(path + GENDER_MODEL, path + GENDER_PROTO)


def generate_face():
    """Request image from "https://thispersondoesnotexist.com/image" and return its content

    Returns:
        bytearray: bytearray of image
    """
    r = requests.get("https://thispersondoesnotexist.com/image")
    return r.content


def detect_face(image: bytearray, confidence_threshold=0.5):
    """Use NN to detect a face in the generate image.

    Args:
        image (bytearray): Image of the generated face
        confidence_threshold (float, optional): Confidence of face in image. Defaults to 0.5.

    Returns:
        np_array: frame
        list: face
    """
    decoded = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
    frame = cv2.resize(decoded, (300, 300), interpolation=cv2.INTER_AREA)
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177.0, 123.0))
    face_net.setInput(blob)
    output = np.squeeze(face_net.forward())
    for i in range(output.shape[0]):
        confidence = output[i, 2]
        if not confidence > confidence_threshold:
            continue

        box = output[i, 3:7] * np.array(
            [frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]]
        )
        start_x, start_y, end_x, end_y = box.astype(int)
        start_x, start_y, end_x, end_y = (
            start_x - 10,
            start_y - 10,
            end_x + 10,
            end_y + 10,
        )
        start_x = 0 if start_x < 0 else start_x
        start_y = 0 if start_y < 0 else start_y
        end_x = 0 if end_x < 0 else end_x
        end_y = 0 if end_y < 0 else end_y
        face = start_x, start_y, end_x, end_y
        return frame, face


def detect_gen_and_age(face, frame):
    """Using NN to detect the gender of person in the image.

    Args:
        face (list): list of x's and y's of face
        frame (np_array): array of image

    Returns:
        str: detected gender of person in image
        str: detected age of person in image
    """
    start_x, start_y, end_x, end_y = face
    face_img = frame[start_y:end_y, start_x:end_x]
    blob = cv2.dnn.blobFromImage(
        image=face_img,
        scalefactor=1.0,
        size=(227, 227),
        mean=MODEL_MEAN_VALUES,
        swapRB=False,
    )
    # Predict Gender
    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    i = gender_preds[0].argmax()
    age_net.setInput(blob)
    j = age_net.forward()[0].argmax()
    return GENDER_LIST[i], AGE_INTERVALS[i]


def personal_details(gender: str):
    """Using "https://api.namefake.com/" to retrieve random name and address.

    Args:
        gender (str): gender to determine name of random person

    Returns:
        str: name of random person
        str: address of random person
    """
    r = requests.get(f"https://api.namefake.com/{gender.lower()}").json()
    return r["name"], r["address"]


def create_person():
    """Generate completely random image from "https://thispersondoesnotexist.com". Uses NN to esitmate gender and age.
    From gender it will generate a random name and address using ""https://api.namefake.com/".

    Returns:
        dict: {
            name: str,
            gender: str,
            age: int,
            address: str
            image: bytearray
        }
    """
    image = generate_face()
    frame, face = detect_face(image)
    gender, age = detect_gen_and_age(face, frame)
    age_check = age[1:-1].strip().split(",")
    age = randint(int(age_check[0]), int(age_check[1]))
    name, address = personal_details(gender)
    return {
        "name": name,
        "gender": gender,
        "age": age,
        "address": address,
        "image": image,
    }
