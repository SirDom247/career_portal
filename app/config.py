# This file storea sconfiguration variables like Paystack secret keys.
class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYSTACK_SECRET_KEY = 'your_paystack_secret_key'
