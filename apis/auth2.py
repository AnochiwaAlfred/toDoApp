import jwt
import datetime
from ninja import Router, FormEx, Schema, UploadedFile
from ninja.security import HttpBearer
from django.contrib.auth import authenticate, login, logout, get_user_model
from ninja.errors import HttpError
from django.conf import settings
from typing import List, Union
from users.models import *
from users.models.clients import Client as ClientAuth

from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decouple import config
from django.core.files.base import ContentFile
# from django.contrib.auth.hashers import make_password
import pyotp
from plugins.generate_otp import generate_otp
from schemas.auth import *
from plugins.hasher import hasherGenerator
from datetime import datetime, timedelta, timezone
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import smtplib, ssl
from email.message import EmailMessage
from google_auth_oauthlib.flow import Flow
from google_auth_oauthlib import flow as small_flow
from google.auth.transport.requests import AuthorizedSession
from django.contrib.auth.models import User

# Create a router for authentication endpoints
router = Router(tags=["Authentication 2"])

# JWT Secret Key (should be stored in settings.py)
SECRET_KEY = settings.SECRET_KEY

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = CustomUser.objects.get(id=payload["id"])
            return user  # Returning user makes it available in request.auth
        except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
            return None  # Unauthorized

# Function to create access and refresh tokens
def create_jwt_tokens(user):
    access_token_exp = datetime.utcnow() + timedelta(hours=4)  # Access token valid for 4 hours
    refresh_token_exp = datetime.utcnow() + timedelta(days=7)  # Refresh token valid for 7 days

    access_payload = {
        "id": user.id,
        "username": user.username,
        "exp": access_token_exp,
        "iat": datetime.utcnow()
    }
    
    refresh_payload = {
        "id": user.id,
        "exp": refresh_token_exp
    }

    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token

@router.post("/refresh_token")
def refresh_access_token(request, refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user = CustomUser.objects.get(id=payload["id"])
        new_access_token, _ = create_jwt_tokens(user)
        return JsonResponse({"access_token": new_access_token}, status=200)
    except (jwt.ExpiredSignatureError, jwt.DecodeError, CustomUser.DoesNotExist):
        return JsonResponse({"error": "Invalid or expired refresh token"}, status=401)


@router.post("/refresh-token", response=Union[TokenResponse, str, dict])
def refresh_token(request, data: RefreshTokenSchema = FormEx(...)):
    try:
        payload = jwt.decode(data.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user = CustomUser.objects.filter(id=payload["id"]).first()

        if not user:
            return str(HttpError(401, "Invalid refresh token"))

        # Generate a new access token
        new_access_token, _ = create_jwt_tokens(user)

        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        return str(HttpError(401, "Refresh token expired"))
    except jwt.DecodeError:
        return str(HttpError(401, "Invalid refresh token"))



@router.post("/register", response=Union[TokenResponse, str, dict])
def register(request, data: AuthUserRegistrationSchema=FormEx(...)):
    errors = {}

    # Check if username or email already exists
    if ClientAuth.objects.filter(username=data.username).exists():
        errors["username"] = "Username already exists"
    if ClientAuth.objects.filter(email=data.email).exists():
        errors["email"] = "Email already in use"
    if data.password and data.password != data.passwordConfirm:
        errors["password"] = "Passwords do not match"

    if errors:
        # print(errors)
        return JsonResponse({"success": False, "errors": errors}, status=400)
    
    # Create and save the user
    user = ClientAuth.objects.create(
        username=data.username,
        email=data.email,
        phone=data.phone,
    )
    user.set_password(data.password)
    user.save()
    # Generate JWT token
    token = create_jwt_tokens(user)
    print(user)
    return {"token": token, "id": user.id, "username": user.username}
    


@router.post("/login", response=Union[TokenResponse, str, dict])
def login_user(request, data: UserLoginSchema = FormEx(...)):
    user = CustomUser.objects.filter(username=data.username_or_email).first()
    if not user:
        user = CustomUser.objects.filter(email=data.username_or_email).first()
        errors = {"error": "Invalid email or password", "status": 401}
    
    
    if user:
        my_auth = authenticate(request, username=user.username, password=data.password)
        if my_auth:
            login(request, user)
            access_token, refresh_token = create_jwt_tokens(user)
            return {"id": user.id, "username": user.username, "message": "User logged in successfully", "access_token": access_token, "refresh_token": refresh_token}
    
    return JsonResponse({"success": False, "errors": errors}, status=400)
   
    

@router.delete("/deleteUser/{user_id}", auth=JWTAuth())
def delete_user(request, user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return {"error": "User not found"}
    user.delete()
    return {"message": f"User {user.username} deleted successfully"}



@router.post("/logout", auth=None)
def logout_user(request):
    logout(request)
    return {
        "message": "User Logged Out; You can sign in again using your username and password."
    }
    

@router.get("/get_user_image", auth=JWTAuth())
def get_user_image(request):
    user = get_object_or_404(ClientAuth, id=request.auth.id)
    if not user.image:
        return JsonResponse({"success": False, "errors": {"error": "User has no image"}}, status=400)

    image_url = request.build_absolute_uri(user.image.url)
    return JsonResponse({"success": True, "image": image_url})



@router.put("/change_password", auth=JWTAuth(), response=Union[dict, str])
def change_password(request, data: ChangePasswordSchema):
    
    user = request.auth  # The authenticated user from JWT
    if not user.check_password(data.old_password):
        return JsonResponse({"success": False, "error": "Incorrect old password"}, status=400)

    if data.new_password != data.confirm_new_password:
        return JsonResponse({"success": False, "error": "New passwords do not match"}, status=400)

    user.set_password(data.new_password)
    user.save()

    return {"message": "Password changed successfully"}

@router.post("/update_image", auth=JWTAuth(), response={200: dict})
def update_user_image(request, image: UploadedFile = File(...)):
    user_id = request.auth.id  # User authenticated via JWT
    user = ClientAuth.objects.filter(id=user_id).first() 
    if not user:
        raise HttpError(401, "User not a client")
    
    user.image = image
    user.image.save(image.name, ContentFile(image.read()), save=True)
    user.save()
    
    return {"message": "Profile image updated successfully", "image_url": user.image.url}

from django.middleware.csrf import get_token
@router.put("/csrf_token_view", auth=None, response={200: dict})
def csrf_token_view(request):
    return JsonResponse({"csrfToken": get_token(request)})