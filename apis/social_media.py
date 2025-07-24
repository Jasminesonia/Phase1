from fastapi import APIRouter, HTTPException
from datetime import datetime
from io import BytesIO
import base64
import cloudinary
import cloudinary.uploader
import requests
import os
from database.mongo import get_collection
from schemas import SocialMediaRequest

# Environment Variables
cloudinary.config(
    cloud_name=os.getenv("ACLOUD_NAME"),
    api_key=os.getenv("API_KEYS"),
    api_secret=os.getenv("API_SECRET")
)

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKENS = os.getenv("ACCESS_TOKENS")
PAGE_ID = os.getenv("PAGE_ID")
FACEBOOK_ACCESS = os.getenv("FACEBOOK_ACCESS")

# Router instance
router = APIRouter()
social_collection = get_collection("social")


@router.post("/upload-socialmedia/")
async def upload_image(payload: SocialMediaRequest):
    try:
        # Step 1: Decode base64 image
        try:
            image_data = base64.b64decode(payload.base64_image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")

        image_file = BytesIO(image_data)

        # Step 2: Upload to Cloudinary
        result = cloudinary.uploader.upload(image_file)
        result["uploaded_at"] = datetime.utcnow()

        image_url = result.get("secure_url")
        if not image_url:
            raise HTTPException(status_code=500, detail="Image URL not returned from Cloudinary")

        # Step 3: Post to Instagram
        container_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"
        container_payload = {
            "image_url": image_url,
            "caption": payload.caption,
            "access_token": ACCESS_TOKENS
        }
        container_res = requests.post(container_url, data=container_payload).json()
        if 'id' not in container_res:
            raise HTTPException(status_code=400, detail=f"Instagram media creation failed: {container_res}")

        publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": container_res['id'],
            "access_token": ACCESS_TOKENS
        }
        insta_response = requests.post(publish_url, data=publish_payload).json()

        # Step 4: Post to Facebook
        fb_url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/photos"
        fb_payload = {
            "url": image_url,
            "caption": payload.caption,
            "access_token": FACEBOOK_ACCESS
        }
        fb_response = requests.post(fb_url, data=fb_payload).json()

        # Step 5: Save to MongoDB
        full_record = {
            "caption": payload.caption,
            "uploaded_at": datetime.utcnow(),
            "cloudinary_response": result,
            "instagram_response": insta_response,
            "facebook_response": fb_response
        }

        insert_result = await social_collection.insert_one(full_record)
        full_record["_id"] = str(insert_result.inserted_id)

        return {
            "message": "Upload and posting successful",
            "data": full_record
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")
