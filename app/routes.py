# This file handles routing and API logic (forms, payments, etc.).
from app import app, db
from flask import render_template, request, redirect, url_for
from app.models import Beneficiary, Facilitator, JobPosting, Event, Resource
import requests
from flask_security import login_required, current_user
from app.utils import send_otp, verify_user_otp

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Beneficiary Registration
@app.route('/register-beneficiary', methods=['GET', 'POST'])
def register_beneficiary():
    if request.method == 'POST':
        name = request.form['name']
        career_interests = request.form['career_interests']
        new_beneficiary = Beneficiary(name=name, career_interests=career_interests)
        db.session.add(new_beneficiary)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_beneficiary.html')

# Facilitator Registration
@app.route('/register-facilitator', methods=['GET', 'POST'])
def register_facilitator():
    if request.method == 'POST':
        name = request.form['name']
        expertise = request.form['expertise']
        new_facilitator = Facilitator(name=name, expertise=expertise)
        db.session.add(new_facilitator)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_facilitator.html')

# Job Posting
@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        job_title = request.form['job_title']
        description = request.form['description']
        location = request.form['location']
        new_job = JobPosting(job_title=job_title, description=description, location=location)
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post_job.html')

# Paystack Payment Integration
@app.route('/paystack', methods=['POST'])
def paystack_payment():
    amount = request.form['amount']
    email = request.form['email']
    
    headers = {
        'Authorization': 'Bearer your_paystack_secret_key',
    }
    data = {
        'email': email,
        'amount': amount,
        'currency': 'NGN',
    }
    response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=data)
    payment_data = response.json()
    return redirect(payment_data['data']['authorization_url'])

# OTP Verification
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        if verify_user_otp(current_user, otp):  # Implement OTP verification function
            return redirect(url_for('index'))
    return render_template('verify_otp.html')
