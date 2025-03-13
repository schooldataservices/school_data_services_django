#!/bin/bash

# Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-file.json"
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-file.json"' >> ~/.bashrc
source ~/.bashrc

# Authenticate with gcloud
gcloud auth login
gcloud config set project your-project-id
