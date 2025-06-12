from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from .gcs_storage import CustomGoogleCloudStorage  # Assuming this is where your custom storage class is defined

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', storage=CustomGoogleCloudStorage())

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        print(f"self.image: {self.image}")  # Check if an image is assigned
        print(f"self.image.name: {self.image.name if self.image else 'None'}")  # Check if the name exists

        # Ensure an image is assigned before saving
        if not self.image or not self.image.name:
            # print("No profile image found, using default.")
            self.image = "profile_pics/default.jpg"

        # Update user and image field if existing instance of Profile model, otherwise update
        super().save(*args, **kwargs)

        gcs_path = self.image.name.replace('\\', '/')  # Ensure the file path uses forward slashes
        # print(f"gcs_path: {gcs_path}")

        # Skip processing if the image is the default one
        if gcs_path == "profile_pics/default.jpg":
            # print("Default image detected. Skipping resizing logic.")
            return

        try:
            # Open and read the image file using the storage backend
            with self.image.open('rb') as gcs_file:
                image_content = gcs_file.read()

            img = Image.open(BytesIO(image_content))

            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize the image if necessary
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)

                # Save the resized image back to the same path in GCS
                img_bytes = BytesIO()
                img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)

                # Save the resized image back to the storage (GCS)
                self.image.save(gcs_path, ContentFile(img_bytes.read()))
                print(f"Resized image saved to {gcs_path}.")

        except FileNotFoundError:
            print(f"File {gcs_path} not found in Google Cloud Storage.")
        except AttributeError:
            print("AttributeError: Image object is None, skipping resizing.")
        except Exception as e:
            print(f"Unexpected error while processing the profile image: {e}")
