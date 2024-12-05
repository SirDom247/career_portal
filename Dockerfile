FROM python:3.8-slim

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Install dependencies
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Expose port and run the application
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
