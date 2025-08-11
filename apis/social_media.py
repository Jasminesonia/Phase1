from bson import ObjectId
from fastapi import APIRouter, HTTPException
from datetime import datetime
from io import BytesIO
import base64
import cloudinary
import cloudinary.uploader
import requests
import os
from database.mongo import get_collection
from schemas import SocialMediaRequest, TenantData, InstaCredentials, FacebookCredentials

# Environment Variables
cloudinary.config(
    cloud_name=os.getenv("ACLOUD_NAME"),
    api_key=os.getenv("API_KEYS"),
    api_secret=os.getenv("API_SECRET")
)

# IG_USER_ID = os.getenv("IG_USER_ID")
# ACCESS_TOKENS = os.getenv("ACCESS_TOKENS")
# PAGE_ID = os.getenv("PAGE_ID")
# FACEBOOK_ACCESS = os.getenv("FACEBOOK_ACCESS")

# Router instance
router = APIRouter()
social_collection = get_collection("social")
tenant_collection = get_collection("tenant")


@router.post("/save-instagram-credentials/")
async def save_instagram_credentials(data: InstaCredentials):
    try:
        # Check if document exists for this user
        existing = await tenant_collection.find_one({"user_id": ObjectId(data.user_id)})
        if existing:
            # Update only Instagram credentials
            await tenant_collection.update_one(
                {"user_id": ObjectId(data.user_id)},
                {"$set": {
                    "insta_credentials": {
                        "ACCESS_TOKENS": data.ACCESS_TOKENS,
                        "IG_USER_ID": data.IG_USER_ID
                    }
                }}
            )
            return {"message": "Instagram credentials updated successfully"}
        else:
            # Create new document with Instagram credentials
            document = {
                "user_id": ObjectId(data.user_id),
                "insta_credentials": {
                    "ACCESS_TOKENS": data.ACCESS_TOKENS,
                    "IG_USER_ID": data.IG_USER_ID
                },
                "created_at": datetime.utcnow()
            }
            result = await tenant_collection.insert_one(document)
            return {"message": "Instagram credentials saved", "id": str(result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-instagram-credentials/{user_id}")
async def get_instagram_credentials(user_id: str):
    try:
        # Look for the document with the given user_id
        existing = await tenant_collection.find_one({"user_id": ObjectId(user_id)})

        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        # Extract Instagram credentials if present
        insta_credentials = existing.get("insta_credentials")
        if not insta_credentials:
            raise HTTPException(status_code=404, detail="Instagram credentials not found")

        return {
            "user_id": str(existing["user_id"]),
            "insta_credentials": insta_credentials
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-facebook-credentials/")
async def save_facebook_credentials(data: FacebookCredentials):
    try:
        # Check if document exists for this user
        existing = await tenant_collection.find_one({"user_id": ObjectId(data.user_id)})
        if existing:
            # Update only Facebook credentials
            await tenant_collection.update_one(
                {"user_id": ObjectId(data.user_id)},
                {"$set": {
                    "facebook_credentials": {
                        "PAGE_ID": data.PAGE_ID,
                        "FACEBOOK_ACCESS": data.FACEBOOK_ACCESS
                    }
                }}
            )
            return {"message": "Facebook credentials updated successfully"}
        else:
            # Create new document with Facebook credentials
            document = {
                "user_id": ObjectId(data.user_id),
                "facebook_credentials": {
                    "PAGE_ID": data.PAGE_ID,
                    "FACEBOOK_ACCESS": data.FACEBOOK_ACCESS
                },
                "created_at": datetime.utcnow()
            }
            result = await tenant_collection.insert_one(document)
            return {"message": "Facebook credentials saved", "id": str(result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-facebook-credentials/{user_id}")
async def get_facebook_credentials(user_id: str):
    try:
        # Search for the document with the given user_id
        existing = await tenant_collection.find_one({"user_id": ObjectId(user_id)})

        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        # Extract Facebook credentials if available
        fb_credentials = existing.get("facebook_credentials")
        if not fb_credentials:
            raise HTTPException(status_code=404, detail="Facebook credentials not found")

        return {
            "user_id": str(existing["user_id"]),
            "facebook_credentials": fb_credentials
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/edit-instagram-credentials/")
async def edit_instagram_credentials(data: InstaCredentials):
    try:
        existing = await tenant_collection.find_one({"user_id": ObjectId(data.user_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="User credentials not found")

        update_result = await tenant_collection.update_one(
            {"user_id": ObjectId(data.user_id)},
            {"$set": {
                "insta_credentials.ACCESS_TOKENS": data.ACCESS_TOKENS,
                "insta_credentials.IG_USER_ID": data.IG_USER_ID
            }}
        )

        if update_result.modified_count == 0:
            return {"message": "No changes made"}
        return {"message": "Instagram credentials updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/edit-facebook-credentials/")
async def edit_facebook_credentials(data: FacebookCredentials):
    try:
        existing = await tenant_collection.find_one({"user_id": ObjectId(data.user_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="User credentials not found")

        update_result = await tenant_collection.update_one(
            {"user_id": ObjectId(data.user_id)},
            {"$set": {
                "facebook_credentials.PAGE_ID": data.PAGE_ID,
                "facebook_credentials.FACEBOOK_ACCESS": data.FACEBOOK_ACCESS
            }}
        )

        if update_result.modified_count == 0:
            return {"message": "No changes made"}
        return {"message": "Facebook credentials updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-credentials/")
async def save_credentials(data: TenantData):
    try:
        # Check if credentials already exist for the user
        existing = await tenant_collection.find_one({"user_id": ObjectId(data.user_id)})
        if existing:
            raise HTTPException(status_code=409, detail="Credentials already exist for this user")

        document = {
            "user_id": ObjectId(data.user_id),
            "insta_credentials": {
                "ACCESS_TOKENS": data.insta_credentials.ACCESS_TOKENS if data.insta_credentials else None,
                "IG_USER_ID": data.insta_credentials.IG_USER_ID if data.insta_credentials else None
            },
            "facebook_credentials": {
                "PAGE_ID": data.facebook_credentials.PAGE_ID if data.facebook_credentials else None,
                "FACEBOOK_ACCESS": data.facebook_credentials.FACEBOOK_ACCESS if data.facebook_credentials else None
            },
            "created_at": datetime.utcnow()
        }

        result = await tenant_collection.insert_one(document)
        return {"message": "Credentials saved successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-credentials/{user_id}")
async def get_credentials(user_id: str):
    try:
        # Search for the document with this user_id
        existing = await tenant_collection.find_one({"user_id": ObjectId(user_id)})

        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": str(existing["user_id"]),
            "insta_credentials": existing.get("insta_credentials"),
            "facebook_credentials": existing.get("facebook_credentials"),
            "created_at": existing.get("created_at")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update-credentials/")
async def update_credentials(data: TenantData):
    try:
        user_obj_id = ObjectId(data.user_id)

        update_fields = {}

        if data.insta_credentials:
            if data.insta_credentials.ACCESS_TOKENS is not None:
                update_fields["insta_credentials.ACCESS_TOKENS"] = data.insta_credentials.ACCESS_TOKENS
            if data.insta_credentials.IG_USER_ID is not None:
                update_fields["insta_credentials.IG_USER_ID"] = data.insta_credentials.IG_USER_ID

        if data.facebook_credentials:
            if data.facebook_credentials.PAGE_ID is not None:
                update_fields["facebook_credentials.PAGE_ID"] = data.facebook_credentials.PAGE_ID
            if data.facebook_credentials.FACEBOOK_ACCESS is not None:
                update_fields["facebook_credentials.FACEBOOK_ACCESS"] = data.facebook_credentials.FACEBOOK_ACCESS

        if not update_fields:
            raise HTTPException(status_code=400, detail="No credentials provided to update")

        update_fields["updated_at"] = datetime.utcnow()

        result = await tenant_collection.update_one(
            {"user_id": user_obj_id},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Credentials not found for the given user")

        return {"message": "Credentials updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-socialmedia/")
async def upload_image(payload: SocialMediaRequest):
    try:
        # Step 1: Fetch credentials from tenant collection based on user_id
        try:
            user_obj_id = ObjectId(payload.user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid user_id format")

        tenant = await tenant_collection.find_one({"user_id": user_obj_id})
        if not tenant:
            raise HTTPException(status_code=404, detail="Credentials for this user not found")

        insta_creds = tenant.get("insta_credentials", {})
        fb_creds = tenant.get("facebook_credentials", {})

        IG_USER_ID = insta_creds.get("IG_USER_ID")
        ACCESS_TOKENS = insta_creds.get("ACCESS_TOKENS")
        PAGE_ID = fb_creds.get("PAGE_ID")
        FACEBOOK_ACCESS = fb_creds.get("FACEBOOK_ACCESS")

        if not all([IG_USER_ID, ACCESS_TOKENS, PAGE_ID, FACEBOOK_ACCESS]):
            raise HTTPException(status_code=400, detail="Incomplete social media credentials")

        # Step 2: Decode base64 image
        try:
            image_data = base64.b64decode(payload.base64_image)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")

        image_file = BytesIO(image_data)

        # Step 3: Upload to Cloudinary
        result = cloudinary.uploader.upload(image_file)
        result["uploaded_at"] = datetime.utcnow()

        image_url = result.get("secure_url")
        if not image_url:
            raise HTTPException(status_code=500, detail="Image URL not returned from Cloudinary")

        # Step 4: Post to Instagram
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

        # Step 5: Post to Facebook
        fb_url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/photos"
        fb_payload = {
            "url": image_url,
            "caption": payload.caption,
            "access_token": FACEBOOK_ACCESS
        }
        fb_response = requests.post(fb_url, data=fb_payload).json()

        # Step 6: Save to MongoDB
        full_record = {
            "user_id": user_obj_id,
            "caption": payload.caption,
            "uploaded_at": datetime.utcnow(),
            "cloudinary_response": result,
            "instagram_response": insta_response,
            "facebook_response": fb_response
        }

        insert_result = await social_collection.insert_one(full_record)

        # Convert ObjectId to string for return
        full_record["_id"] = str(insert_result.inserted_id)
        full_record["user_id"] = str(full_record["user_id"])

        return {
            "message": "Upload and posting successful",
            "data": full_record
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")

# @router.post("/upload-socialmedia/")
# async def upload_image(payload: SocialMediaRequest):
#     try:
#         # Step 1: Decode base64 image
#         try:
#             image_data = base64.b64decode(payload.base64_image)
#         except Exception:
#             raise HTTPException(status_code=400, detail="Invalid base64 image data")
#
#         image_file = BytesIO(image_data)
#
#         # Step 2: Upload to Cloudinary
#         result = cloudinary.uploader.upload(image_file)
#         result["uploaded_at"] = datetime.utcnow()
#
#         image_url = result.get("secure_url")
#         if not image_url:
#             raise HTTPException(status_code=500, detail="Image URL not returned from Cloudinary")
#
#         # Step 3: Post to Instagram
#         container_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media"
#         container_payload = {
#             "image_url": image_url,
#             "caption": payload.caption,
#             "access_token": ACCESS_TOKENS
#         }
#         container_res = requests.post(container_url, data=container_payload).json()
#         if 'id' not in container_res:
#             raise HTTPException(status_code=400, detail=f"Instagram media creation failed: {container_res}")
#
#         publish_url = f"https://graph.facebook.com/v23.0/{IG_USER_ID}/media_publish"
#         publish_payload = {
#             "creation_id": container_res['id'],
#             "access_token": ACCESS_TOKENS
#         }
#         insta_response = requests.post(publish_url, data=publish_payload).json()
#
#         # Step 4: Post to Facebook
#         fb_url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/photos"
#         fb_payload = {
#             "url": image_url,
#             "caption": payload.caption,
#             "access_token": FACEBOOK_ACCESS
#         }
#         fb_response = requests.post(fb_url, data=fb_payload).json()
#
#         # Step 5: Save to MongoDB
#         full_record = {
#             "caption": payload.caption,
#             "uploaded_at": datetime.utcnow(),
#             "cloudinary_response": result,
#             "instagram_response": insta_response,
#             "facebook_response": fb_response
#         }
#
#         insert_result = await social_collection.insert_one(full_record)
#         full_record["_id"] = str(insert_result.inserted_id)
#
#         return {
#             "message": "Upload and posting successful",
#             "data": full_record
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")
