from django.conf import settings
from django.core.files.storage import Storage
from google.cloud import storage
import json
from google.oauth2 import service_account
from emailscraper_proj.settings import django_hosting_json_file

# Authentication
def get_gcs_client():
    """Returns an authenticated GCS client."""
    gs_credentials_info = json.loads(django_hosting_json_file)
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(gs_credentials_info)
    return storage.Client(credentials=GS_CREDENTIALS, project=GS_CREDENTIALS.project_id)

# To work with models
class CustomGoogleCloudStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.client = get_gcs_client()  # Use the centralized GCS client
        self.bucket = self.client.bucket(settings.GS_BUCKET_NAME)
        super().__init__(*args, **kwargs)
    
    def _save(self, name, content):
        # Ensure the file path uses forward slashes
        name = name.replace('\\', '/')
        
        blob = self.bucket.blob(name)
        
        # Check if content_type is available, otherwise use a default
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        
        # Upload using file-like object (ContentFile)
        blob.upload_from_file(content, content_type=content_type)
        return name

    def url(self, name):
        return f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{name}"

    def exists(self, name):
        """Check if the file exists in Google Cloud Storage."""
        blob = self.bucket.blob(name)
        return blob.exists()

# Upload raw data (such as text, JSON, or binary data that isn't tied to a Django model).
def upload_to_gcs(bucket_name, file_path, file_content, content_type):
    """Uploads a file (data) to Google Cloud Storage and returns the public URL."""
    client = get_gcs_client()  # Reuse the client here
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    
    # Upload using the raw file content
    blob.upload_from_string(file_content, content_type=content_type)
    
    return blob.public_url

def file_exists_in_gcs(bucket_name, file_path):
    """Checks if a file exists in Google Cloud Storage."""
    client = get_gcs_client()  # Reuse the client here
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    return blob.exists()



