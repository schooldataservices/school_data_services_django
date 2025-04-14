# Build stage
FROM python:3.9-slim-buster AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    default-libmysqlclient-dev

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Final stage
FROM python:3.9-slim-buster

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

ENV DJANGO_SETTINGS_MODULE=emailscraper_proj.settings
ENV PORT=8080

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "60", "--workers", "2", "emailscraper_proj.wsgi:application"]



#Manually call before
# Run migrations to update the database schema
# python manage.py migrate --noinput

# Collect static files for production use
# python manage.py collectstatic --noinput


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