import hashlib
import os
from datetime import datetime, timedelta
from random import randbytes, randint
# from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Body, Response, Depends
from fastapi_jwt_auth import AuthJWT
from config import settings
from database.mongo import get_collection
from emailsetup.verifyEmail import ForgotPassEmail
from schemas import UserSignupSchema, UserSigninSchema, ForgotPasswordSchema, ResetPasswordSchema, \
    UpdatePasswordSchema, VerifyOTPSchema
from utils import hash_password, verify_password
from jwt_config import get_jwt_config

router = APIRouter()
Users = get_collection("users_info")

ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 30))
REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 1440))  # default: 1 day


@router.post("/signup")
async def signup_user(payload: UserSignupSchema):
    # 1. Check if user already exists using Gmail
    existing_user = await Users.find_one({"email": payload.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    # 2. Password confirmation check
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password doesn't match"
        )

    # 3. Prepare and insert user data
    user_info = payload.dict()
    del user_info["passwordConfirm"]

    user_info.update({
        "role": "user",
        "verified": False,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "password": hash_password(payload.password)
    })

    result = await Users.insert_one(user_info)
    return {"status": "success", "user_id": str(result.inserted_id)}


@router.post("/signin")
async def users_signin(payload: UserSigninSchema, response: Response, Authorize: AuthJWT = Depends()):
    # Check if the user exists
    db_user = await Users.find_one({"email": payload.email})
    print("db user", db_user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email",
        )
    if db_user:
        if not verify_password(payload.password, db_user["password"]):
            if not payload.password:
                raise HTTPException(detail="User not found")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect Password",
            )
        if db_user["status"] == "inactive":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your account is not active, please contact the administrator",
            )

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(db_user["_id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(db_user["_id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )

    # Send both access
    return {
        "access_token": access_token,
        "role": db_user.get("role", ""),  # Use get to avoid KeyError
        "verified": db_user.get("verified", False),  # Use get to avoid KeyError
        "user_email": db_user.get("email", ""),  # Use get to avoid KeyError
        "user_id": str(db_user["_id"]),
    }


@router.post("/verify")
async def verify_otp(payload: VerifyOTPSchema):
    db_user = await Users.find_one({"email": payload.email})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if "verification_code" not in db_user or db_user["verification_code"] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP found. Please request a new one."
        )

    if db_user["verification_code"] != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP."
        )

    # Clear the verification_code and optionally mark the user as verified
    await Users.find_one_and_update(
        {"email": payload.email},
        {
            "$set": {
                "verified": True,
                "verification_code": None,
                "updated_at": datetime.utcnow()
            }
        },
    )

    return {
        "status": "success",
        "message": "OTP verification successful. You can now sign in."
    }


@router.post("/forgotPass")
async def forgot_pass(payload: ForgotPasswordSchema):
    if payload.email == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Email"
        )
    existing = await Users.find_one({"email": payload.email})
    print(existing)
    if existing:
        try:

            verification_code = str(randint(100000, 999999))
            await Users.find_one_and_update(
                {"email": payload.email},
                {
                    "$set": {
                        "verification_code": verification_code,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            await ForgotPassEmail(
                existing["name"], verification_code, [payload.email]
            ).sendVerificationCode()
        except Exception as error:
            print(error)
            await Users.find_one_and_update(
                {"email": payload.email},
                {"$set": {"verification_code": None, "updated_at": datetime.utcnow()}},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error sending email setup",
            )
    return {
        "status": "success",
        "message": "Password reset code successfully sent to your email setup",
    }


@router.post("/resetPass")
async def reset_pass(payload: ResetPasswordSchema, Authorize: AuthJWT = Depends()):
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    user = await Users.find_one({"email": payload.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Optional: check that user has verified OTP recently (if using a verified flag)
    if not user.get("verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before resetting password"
        )

    hashed_password = hash_password(payload.password)

    try:
        await Users.find_one_and_update(
            {"_id": user["_id"]},
            {
                "$set": {
                    "password": hashed_password,
                    "updated_at": datetime.utcnow(),
                    "verification_code": None  # clear old OTP if any
                }
            }
        )
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while resetting password"
        )

    # Auto-login: generate tokens
    access_token = Authorize.create_access_token(
        subject=str(user["_id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )
    refresh_token = Authorize.create_refresh_token(
        subject=str(user["_id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )

    return {
        "status": "success",
        "message": "Password reset successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", ""),
        "verified": user.get("verified", False)
    }


@router.post("/updatePass")
async def update_pass(payload: UpdatePasswordSchema):
    if len(payload.oldPassword.strip()) <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Old Password should not be empty"
        )
    elif len(payload.password.strip()) <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password should not be empty"
        )
    elif payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password doesn't match"
        )
    existing = await Users.find_one({"email": payload.email})
    if existing:
        user_info = payload.dict()

        if not verify_password(payload.oldPassword, existing["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password"
            )
        user_info["password"] = hash_password(payload.password)
        try:
            await Users.find_one_and_update(
                {"email": payload.email},
                {
                    "$set": {
                        "password": hash_password(payload.password),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
        except Exception as error:
            print(error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There was an error in reset password",
            )
    return {
        "status": "success",
        "message": "Password updated successfully",
    }
