from django.db import models
from django.contrib.auth.models import User
from storages.backends.gcloud import GoogleCloudStorage
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', storage=GoogleCloudStorage())

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Save the original image first
        super().save(*args, **kwargs)

        # Open the image using PIL
        img = Image.open(self.image)

        # Resize the image if necessary
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)

            # Save the resized image to a BytesIO object
            img_io = BytesIO()
            img.save(img_io, format=img.format)
            img_content = ContentFile(img_io.getvalue(), self.image.name)

            # Save the resized image back to the model
            self.image.save(self.image.name, img_content, save=False)

        # Save the model again to ensure the resized image is saved
        super().save(*args, **kwargs)






