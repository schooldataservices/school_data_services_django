from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
from io import BytesIO


class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs): 
        # Ensure an image is assigned before saving
        if not self.image or not self.image.name:
            print("No profile image found, using default.")
            self.image = "profile_pics/default.jpg"

        super().save(*args, **kwargs)  # Save the instance first

        gcs_path = self.image.name  
        print(f"gcs_path: {gcs_path}")

        # **Skip processing if the image is the default one**
        if gcs_path == "profile_pics/default.jpg":
            print("Default image detected. Skipping resizing logic.")
            return  # Exit the function early

        try:
            gcs_file = default_storage.open(gcs_path)
            image_content = gcs_file.read()
            
            # Open the image using Pillow
            img = Image.open(BytesIO(image_content))

            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize the image if necessary
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)

                # Save the resized image back to Google Cloud Storage
                img_bytes = BytesIO()
                img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)

                # Save the updated image back to the same path
                default_storage.save(gcs_path, ContentFile(img_bytes.read()))

        except FileNotFoundError:
            print(f"File {gcs_path} not found in Google Cloud Storage.")
        except Exception as e:
            print(f"Unexpected error while processing the profile image: {e}")


