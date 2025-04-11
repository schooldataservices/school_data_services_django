# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Install system dependencies required for MySQL
# Install system dependencies for MySQL and build tools
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Cloud Run
ENV PORT=8080

# Expose the port that Django will run on
EXPOSE 8080

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=emailscraper_proj.settings

# Change the CMD command to run collectstatic before Gunicorn starts
# CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8080 emailscraper_proj.wsgi:application"]
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8080 --timeout 60 --workers 2 emailscraper_proj.wsgi:application"]



# docker build -t gcr.io/django-hosting-427421/django-hosting .
# docker push gcr.io/django-hosting-427421/django-hosting    

# gcloud run deploy django-hosting \
#     --image gcr.io/django-hosting-427421/django-hosting:latest \
#     --platform managed \
#     --region us-central1 \
#     --allow-unauthenticated \
#     --service-account django-project@django-hosting-427421.iam.gserviceaccount.com \
#     --memory 512Mi \
#     --set-env-vars RUNNING_IN_CLOUD=true,DEBUG=False,DB_HOST="35.236.35.240"