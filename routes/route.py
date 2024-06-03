import os
import uuid

import numpy as np
from fastapi import APIRouter, Request, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from pytesseract import pytesseract
from starlette.responses import FileResponse

import app.controllers.version_controller as version_controller
from app.controllers import sentiment_controller, fraud_detection_controller, \
    scan_card_controller, user_controller, event_controller, ktp_controller
from app.helpers.handler import show_model
from app.middleware.middleware import check_jwt_token
import cv2

class TextData(BaseModel):
    text: str

class ImageFile(BaseModel):
    file: UploadFile

OUTPUT_FOLDER = "./public/faces"
UPLOAD_FOLDER_CARD = "./public/cards"
UPLOAD_FOLDER = "./public/uploads"

router = APIRouter()

@router.get("/")
def get_version(request: Request):
    return version_controller.get(request)

@router.post("/api/sentiment-analysis", dependencies=[Depends(check_jwt_token)])
async def post_sentiment(text_data: TextData):
    return sentiment_controller.post(text_data.text)

@router.post("/api/fraud-project-detection", dependencies=[Depends(check_jwt_token)])
async def post_fraud_detection(text_data: TextData):
    return fraud_detection_controller.post(text_data.text)

@router.get("/api/users", dependencies=[Depends(check_jwt_token)])
def get_users(request: Request):
    return user_controller.getlist(request)

@router.get("/api/events", dependencies=[Depends(check_jwt_token)])
def get_events(request: Request):
    return event_controller.getlist(request)

@router.post("/api/scan-card", dependencies=[Depends(check_jwt_token)])
async def post_scan_card(image_file: UploadFile = File(...)):
    # GET FACE IMAGE
    if not image_file.filename:
        return {
            "error_code": 500,
            "message": "File Gambar wajib di isi!"
        }

    # Read the image file once
    file_bytes = await image_file.read()
    image_path = os.path.join(UPLOAD_FOLDER_CARD, image_file.filename)

    # Save the uploaded image
    with open(image_path, "wb") as f:
        f.write(file_bytes)

    # Deteksi wajah
    cascade_path = "data/face/haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    image = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=10, minSize=(30, 30))

    # Pecah setiap wajah yang terdeteksi
    detected_faces = []
    for idx, (x, y, w, h) in enumerate(faces):
        face_image = image[y:y + h, x:x + w]
        output_filename = f"face_{uuid.uuid4().hex[:6]}.jpg"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        cv2.imwrite(output_path, face_image)
        detected_faces.append({
            "name": output_filename,
        })

    # GET DETAIL INFORMATION
    photo = None
    if len(detected_faces) > 0:
        photo = detected_faces[0]["name"]

    img_bb, results = scan_card_controller.getPredictions(image)
    data = {
        "name": " ".join(results.get('NAME', [""])),
        "profession": " ".join(results.get('PROFESSION', [""])),
        "phone": " ".join(results.get('PHONE', [""])),
        "email": " ".join(results.get('EMAIL', [])),
        "web": " ".join(results.get('WEB', [])),
        "address": " ".join(results.get('ADDRESS', [""])),
        "photo": photo
    }
    return show_model(0, "Successfully Get Data", data)

@router.post("/api/predict-fraud-project", dependencies=[Depends(check_jwt_token)])
async def post_fraud_detection(text_data: TextData):
    return fraud_detection_controller.predict(text_data.text)

@router.post("/api/scan-fraud-project", dependencies=[Depends(check_jwt_token)])
async def post_scan_fraud_project(image_file: UploadFile = File(...)):
    # GET FACE IMAGE
    if not image_file.filename:
        return {
            "error_code": 500,
            "message": "File Gambar wajib di isi!"
        }

    # Read the image file once
    file_bytes = await image_file.read()
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)

    # Save the uploaded image
    with open(image_path, "wb") as f:
        f.write(file_bytes)

    return fraud_detection_controller.scan(image_path)

@router.post("/api/scan-ktp-v2", dependencies=[Depends(check_jwt_token)])
async def post_scan_ktp_v2(image_file: UploadFile = File(...)):
    # GET FACE IMAGE
    if not image_file.filename:
        return {
            "error_code": 500,
            "message": "File Gambar wajib di isi!"
        }

    # Read the image file once
    file_bytes = await image_file.read()
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)

    # Save the uploaded image
    with open(image_path, "wb") as f:
        f.write(file_bytes)

    return fraud_detection_controller.scanKtp(image_path)


@router.post("/api/scan-ktp", dependencies=[Depends(check_jwt_token)])
async def post_scan_fraud_project(image_file: UploadFile = File(...)):
    # GET FACE IMAGE
    if not image_file.filename:
        return {
            "error_code": 500,
            "message": "File Gambar wajib di isi!"
        }

    # Read the image file once
    file_bytes = await image_file.read()
    image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)

    # Save the uploaded image
    with open(image_path, "wb") as f:
        f.write(file_bytes)

    return ktp_controller.scan(image_path)

@router.get("/api/file/{file_name}")
async def get_file(file_name: str):

    if not file_name:
        raise HTTPException(status_code=400, detail="Nama file tidak boleh kosong")
    file_path = os.path.join(OUTPUT_FOLDER, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(file_path)