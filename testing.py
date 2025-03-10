import io
import os
import uvicorn
import shutil
import base64
import numpy as np  
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import sessionmaker, declarative_base
from PIL import Image
from ultralytics import YOLO
from cropping_function import process_image

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ImageModel(Base):
    __tablename__ = "IKad-Temp"
    id = Column(Integer, primary_key=True, index=True)
    original_image = Column(LargeBinary, nullable=False)
    cropped_image = Column(LargeBinary, nullable=False)
    x1 = Column(Integer, nullable=False)
    y1 = Column(Integer, nullable=False)
    x2 = Column(Integer, nullable=False)
    y2 = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

# Load the trained model
model_path = r"C:\Users\User\Desktop\FastAPI\best.pt"
model = YOLO(model_path)

@app.post("/image_cropping/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read the uploaded file contents
        contents = await file.read()
        
        # Save the uploaded file to a temporary location
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(contents)

        # Define the model path
        model_path = r"C:\Users\User\Desktop\FastAPI\best.pt"

        # Process the image
        result = process_image(temp_file_path, model_path)

        # Extract the cropped image and coordinates from the result
        cropped_image_path = result["cropped_resized_paths"][0]
        x1, y1, x2, y2 = result["coordinates"][0]

        # Read the cropped image
        with open(cropped_image_path, "rb") as cropped_file:
            cropped_image = cropped_file.read()

        # Save the original and cropped images to the database
        db = SessionLocal()
        db_image = ImageModel(original_image=contents, cropped_image=cropped_image, x1=x1, y1=y1, x2=x2, y2=y2)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        db.close()

        return JSONResponse(status_code=200, content={"message": f"Image processed and saved successfully as {db_image.id}."})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images/{image_id}")
async def get_image(image_id: int):
    db = SessionLocal()
    db_image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    db.close()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Convert the cropped image bytes to a BytesIO object
    cropped_image_io = io.BytesIO(db_image.cropped_image)
    
    # Return the cropped image as a StreamingResponse
    return StreamingResponse(cropped_image_io, media_type="image/jpeg")

@app.delete("/images/{image_id}")
async def delete_image(image_id: int):
    db = SessionLocal()
    db_image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
    if db_image is None:
        db.close()
        raise HTTPException(status_code=404, detail="Image not found")
    db.delete(db_image)
    db.commit()
    db.close()
    return JSONResponse(status_code=200, content={"message": "Image deleted successfully."})
