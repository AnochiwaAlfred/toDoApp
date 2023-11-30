
from datetime import datetime, timedelta, timezone
import pyotp
from users.models.users import CustomUser

 # Generate OTP
def generate_otp(email):
    totp = pyotp.TOTP(pyotp.random_base32())
    user = CustomUser.objects.get(email=email)
    user.otp = totp.now()
    user.otp_created_at = datetime.now()
    user.save()