from django.shortcuts import redirect
from ninja import Router, FormEx
from decouple import config
from ninja.security import HttpBearer
import pyotp
from plugins.generate_otp import generate_otp
from users.models import *
from schemas.auth import *
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import authenticate
from plugins.hasher import hasherGenerator
from datetime import datetime, timedelta, timezone
from typing import List, Union
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import smtplib, ssl
from email.message import EmailMessage
from google_auth_oauthlib.flow import Flow
from google_auth_oauthlib import flow as small_flow
from  google.auth.transport.requests import AuthorizedSession


router = Router(tags=["Authentication"])






@router.get("/")
def get_user(request):
    auth = request.auth

    user = CustomUser.objects.all().filter(token=auth).get()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "code": user.code,
    }

@router.post("/token", auth=None)  # < overriding global auth
def get_token(request, username: str = FormEx(...), password: str = FormEx(...)):
    """
    This will be used as signup request.
    """
    user = authenticate(username=username, password=password)
    if user:
        hh = hasherGenerator()
        string_formatted = hh.get("token").decode("utf-8")
        hh.update(
            {
                # "rsa_duration": 24,
                "token": string_formatted
            }
        )
        CustomUser.objects.all().filter(id=user.id).update(**hh)
        return {"token": hh.get("token")}
    else:return {"token": False}
        # User is authenticated


@router.post("/register-via-email/", auth=None)
def register_user_with_email(
    request,
    password: str,
    passwordConfirm: str,
    user_data: AuthUserRegistrationSchema = FormEx(...),
):
    user = CustomUser.objects.create(**user_data.dict())
    if password==passwordConfirm:
        user.set_password(password)
        user.save()
    return {"Message": f"Registration successful. ID --> {user.id}"}


@router.post("/register-via-google/", auth=None)
def register_user_with_google(request,  scopes: List[str]):
    client_id = config("GOOGLE_OAUTH2_CLIENT_ID")
    client_secret = config("GOOGLE_OAUTH2_CLIENT_SECRET")

    
    flow = Flow.from_client_config(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "scope": ["profile", "email"],
        },  scopes=["profile", "email"],
    )


    def authenticate():
        authorization_url = Flow.authorization_url()

        # Redirect the user to Google to sign in
        return redirect(authorization_url)

    def callback(request):
        authorization_code = request.args.get("code")

        # Exchange the authorization code for an access token
        credentials = Flow.fetch_token(authorization_code=authorization_code)

        # Make a request to the Google People API to retrieve the user's profile information
        people_api = AuthorizedSession(credentials)
        response = people_api.get("https://people.googleapis.com/v1/people/me")

        # Get the user's profile information
        profile = response.json()

        # Return the user's profile information
        return profile

    # Start the Google authentication flow
    if request.method == "GET":
        return authenticate()

    # Exchange the authorization code for an access token and retrieve the user's profile information
    elif request.method == "POST":
        profile = callback(request)

        # Do something with the user's profile information
        print(profile)
        return str(profile)


@router.post("/send-OTP-Email/", auth=None)
def send_otp_email(request, email):
    userInstance = CustomUser.objects.filter(email=email)
    if userInstance.exists():
        generate_otp(email)
        user = userInstance[0]

        email_address = config('SMTP_EMAIL')
        email_password = config('SMTP_PASSWORD')
        port = 465  # This is the default SSL port

        # create email
        msg = EmailMessage()
        msg["Subject"] = "Your OTP for Email Verification"
        msg["From"] = email_address
        msg["To"] = user.email
        msg.set_content(f"Your SpotiPY OTP is: {user.otp}")
        
        if user.is_verified==False:
            # send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(email_address, email_password)
                server.send_message(msg)
            return {"Message": f"OTP Sent. Check email for OTP"}
        else:return {"Message": f"User already verified"}
    else:return {"Error": f"User {email} does not exist."}

@router.post("/send-OTP-SMS/", auth=None)
def send_otp_sms(request, email):
    userInstance = CustomUser.objects.filter(email=email)
    if userInstance.exists():
        generate_otp(email)
        user = userInstance[0]
        # Twilio account credentials
        TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
        TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
        TWILIO_PHONE_NUMBER = config("TWILIO_PHONE_NUMBER")
        
        # Note that if Twilio fails, register for and use Bandwidth API
        
        # Create a Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        if user.is_verified==False:
            # Send the OTP SMS
            try:
                message = client.messages.create(
                    to=f"{user.phone}",
                    from_=TWILIO_PHONE_NUMBER,
                    body=f"Your SpotiPY OTP is: {user.otp}"
                )
                # Print the message ID
                print(message.sid)
                return {"Message": f"OTP Sent. Check sms for OTP"}
            except TwilioRestException as e:
                return {"error": f"Error sending OTP: {e}"}
        else:return {"Message": f"User already verified"}
    else:return {"Error": f"User {email} does not exist."}

@router.post("/verify-otp/", auth=None)
def verify_otp(request, email: str, otp: str):
    user = CustomUser.objects.get(email=email)
    totp = pyotp.TOTP(user.otp)
    if not totp.verify(otp):
        return {"error": "Invalid OTP. Please try again."}

    user_otp_created_at = user.otp_created_at
    utc_otp_created_at = user_otp_created_at.replace(tzinfo=timezone.utc)
    
    if utc_otp_created_at < datetime.now(timezone.utc) - timedelta(minutes=5):
        return {"Message": "OTP has expired. Please request a new one."}
    else:
    # if totp.verify(otp):
        if otp==user.otp:
            user.is_verified = True
            user.is_active = True
            user.otp = ""
            user.save()
            return {"Message": "Email verification successful."}
        else:
            return {"Message": "Invalid OTP. Please try again."}
    
    
# @router.post('/akjakjbska')
# def asnajsndak(request, email, phone):
#     user = CustomUser.objects.get(email=email)
#     user.phone = phone
#     user.save()
#     return f"{user.phone}"


@router.post("/requestForgotPassword/{email}", auth=None)
def request_forgot_password(request, email:str):
    userInstance = CustomUser.objects.filter(email=email)
    if userInstance.exists():
        generate_otp(email)
        user = userInstance[0]

        email_address = config('SMTP_EMAIL')
        email_password = config('SMTP_PASSWORD')
        port = 465  # This is the default SSL port

        # create email
        msg = EmailMessage()
        msg["Subject"] = "Your OTP for Email Verification"
        msg["From"] = email_address
        msg["To"] = user.email
        msg.set_content(f"Your SpotiPY OTP is: {user.otp}")
        
        # send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email_address, email_password)
            server.send_message(msg)
        return {"Message": f"OTP Sent. Check email for OTP"}
    else:return {"Error": f"User {email} does not exist."}


@router.post("/resetForgotPassword/{email}/", auth=None)
def reset_forgot_password(request, email:str, otp:str, password1:str, password2:str):
    userInstance = CustomUser.objects.filter(email=email)
    if userInstance.exists():
        user = userInstance[0]
        totp = pyotp.TOTP(user.otp)
        if not totp.verify(otp):
            return {"Error": "Invalid OTP. Please try again."}

        user_otp_created_at = user.otp_created_at
        utc_otp_created_at = user_otp_created_at.replace(tzinfo=timezone.utc)
        
        if utc_otp_created_at < datetime.now(timezone.utc) - timedelta(minutes=5):
            return {"Message": "OTP has expired. Please request a new one."}
        
        if otp==user.otp:
            if password1==password2:
                user.set_password(password1)
                user.is_verified = True
                user.is_active = True
                user.otp = ""
                user.save()
                return {"Message": "Email verification successful."}
            else:return {"Error":"Password mismatch"}
        else:return {"Error": "Invalid OTP. Please try again."}
           


# @router.post("/requestForgotPassword/{email}", auth=None)
# def requestforgotpassword(request, email:str):
#     meta =  request.META
#     user = CustomUser.objects.all()

#     if user.filter(email=email).exists():
#         user = CustomUser.objects.all().filter(email=email).get()
#         resetLink =  f"{meta.get('wsgi.url_scheme')}://{meta.get('HTTP_HOST')}/api/v1/auth/resetForgotPassword/{email}/"

#         user.token = numbershuffler() # this a plugin for generating digit code.
#         user.save()
#         # on production check
#         recipent_list =  f"{email}" if config('ENVIRONMENT') == "production" else "anointedngeorge@gmail.com"
#         em = sendUserEmail(
#             recipient_list=recipent_list,
#             subject='Password Reset',
#             context={
#                     'email': email,
#                     'message_date':timezone.now(),
#                     'resetLink':resetLink,
#                     'token':user.token
#                 },
#                 template='forgot_password_reset.html'
#             )
#         return em
#     else:
#         return "Email Does not exist."


# @router.post("/resetForgotPassword/{email}/", auth=None)
# def reset_forgot_password(request, email:str, data:AuthResetPassword=FormEx(...)):
#     fmData = data.dict()
#     user = CustomUser.objects.all()
#     # will check if token exists
#     if user.filter(email=email).exists(): # true or false

#         if user.filter(token=fmData.token).exists(): # true or false
#             if fmData.new_password == fmData.repeat_password:
#                 user.filter(email=email).get()
#                 user.set_password(fmData.new_password) # set the new password
#                 user.isPassRequest = False # reset password request to false
#                 user.token = "" # reset token to ""
#                 user.save() # save
#                 em = sendUserEmail(
#                     recipient_list=f"{email}",
#                     subject='Password Reset',
#                     context={
#                             'email': email,
#                             'message_date':timezone.now(),
#                         },
#                         template='password_confirmation.html'
#                     )
#                 return {"Message":"Password successfully changed."}

#             else:return {"Message":"Password does not match."}

#         else:return {"Message":"Token does not match."}

#     else:return {"Message":"User does not match."}


@router.post("/logout")
def logout(request):
    auth = request.auth
    user = CustomUser.objects.all().filter(token=auth)
    user.update(**{"token": "", "key": ""})
    return {
        "message": "User Logged Out; You can sign in again using your username and password."
    }


@router.post("createSuperUser", response=AuthUserRetrievalSchema)
def createSuperUser(
    request, password: str, data: AuthUserRegistrationSchema = FormEx(...)
):
    authuser = CustomUser.objects.create(**data.dict())
    if authuser:
        authuser.set_password(password)
        authuser.is_active = True
        authuser.is_staff = True
        authuser.is_superuser = True
        authuser.save()
    return authuser


@router.get("/getAllUsers", response=List[AuthUserRetrievalSchema])
def getAllUsers(request):
    users = CustomUser.objects.all()
    return users


User = get_user_model()


@router.post("/logint/")
def login_usert(request, data: UserLoginSchema = FormEx(...)):
    user = authenticate(request, username=data.email, password=data.password)

    if user is not None:
        user2 = CustomUser.objects.get(email=data.email)
        if user2.is_verified == True:
            login(request, user)
            return {"detail": "User logged in successfully"}
        else:
            return {"detail": "User not verified"}

    return {"detail": "Invalid credentials"}


@router.delete("/deleteUser/{user_id}")
def delete_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.delete()
    return f"User {user.username} deleted successfully"




class BearerToken(HttpBearer):
    def authenticate(self, request, token):
        # Validate the token (e.g., using Django's authentication system)
        user = authenticate(request, token=token)
        if user:
            return user
        
@router.post("/login")
def login_user(request, email: str, password: str):
    validate = CustomUser.objects.filter(email=email)
    if validate:
        validated = validate[0].username
        user = authenticate(request, username=validated, password=password)
        if user:
            # User is authenticated
            login(request, user)  # Log the user in
            # Generate an access token (JWT) and return it to the frontend
            # You can use a library like PyJWT to create the token
            hh = hasherGenerator()
            access_token = hh.get("token").decode("utf-8")
            hh.update(
                {
                    # "rsa_duration": 24,
                    "token": access_token
                }
            )
            # CustomUser.objects.all().filter(id=user.id).update(**hh)
            user2 = CustomUser.objects.all().filter(id=user.id)
            user2[0].token=access_token
            user.save()
            print(access_token)
            return {"access_token": access_token, "user_id":user.id}
            # return {"access_token": hh.get("token")}
        else:
            return {"error": "Invalid credentials"}
    else:
        return {"error": "Invalid Email"}
