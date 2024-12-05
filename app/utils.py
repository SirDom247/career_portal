# This file contains utility functions for OTP and payment handling.
import random
import smtplib

# Send OTP to user's email
def send_otp(email):
    otp = random.randint(100000, 999999)
    # Code for sending OTP email (SMTP setup)

# Verify OTP function (pseudo-code)
def verify_user_otp(user, otp_input):
    return user.otp == otp_input  # This is a simplified check
