from google.cloud import secretmanager

def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    Fetches a secret from Google Cloud Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    
    # Build the secret resource name
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    
    # Access the secret
    response = client.access_secret_version(name=name)
    
    # Decode the payload
    secret_value = response.payload.data.decode("UTF-8")
    
    return secret_value
