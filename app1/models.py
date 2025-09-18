from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils.text import slugify
music_storage = MediaCloudinaryStorage(resource_type='raw')


class State_details(models.Model):
    STATE_CHOICES = [
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Karnataka", "Karnataka"),
        ("Kerala", "Kerala"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("West Bengal", "West Bengal"),
        ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
        ("Chandigarh", "Chandigarh"),
        ("Dadra and Nagar Haveli and Daman and Diu", "Dadra and Nagar Haveli and Daman and Diu"),
        ("Delhi", "Delhi"),
        ("Jammu and Kashmir", "Jammu and Kashmir"),
        ("Ladakh", "Ladakh"),
        ("Lakshadweep", "Lakshadweep"),
        ("Puducherry", "Puducherry"),
    ]
    slug = models.SlugField(unique=True, blank=True)  # ✅ added slug
    state_name = models.CharField(max_length=50, choices=STATE_CHOICES, unique=True)
    state_image = models.ImageField(null=True, blank=True, upload_to='state_images', storage=MediaCloudinaryStorage())
    state_description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # auto-generate slug only if not set
            self.slug = slugify(self.state_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.state_name

    
class StateMusic(models.Model):
    state = models.ForeignKey(State_details, on_delete=models.CASCADE, related_name="music")
    title = models.CharField(max_length=100)
    music_file = models.FileField(upload_to="state_music/", storage=music_storage, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.state.state_name}"


class StateFestival(models.Model):
    state = models.ForeignKey(State_details, on_delete=models.CASCADE, related_name="festivals")

    image = models.ImageField(upload_to='festival_images/', storage=MediaCloudinaryStorage(), blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Festival - {self.state.state_name}"





class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    avatar = models.ImageField(
        null=True, blank=True, upload_to='profile_picture', storage=MediaCloudinaryStorage()
    )
    bio = models.TextField(blank=True, null=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    username = models.CharField(max_length=100, blank=True, null=True, default='')

    def __str__(self):
        return self.email
    

from django.db import models
class CommunityData(models.Model):
    CATEGORY_CHOICES = [
        ("heritage_site", "Heritage Site"),
        ("tourist_place", "Tourist Place"),
        ("traditional_shop", "Traditional Shop"),
        ("festival", "Festival"),
        ("food", "Food & Cuisine"),
    ]

    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="community_posts")
    state = models.ForeignKey("State_details", on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=100)


    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="heritage_site")

    image = models.ImageField(null=True, blank=True, upload_to='community_images', storage=MediaCloudinaryStorage())
    description = models.TextField()

    likes = models.PositiveIntegerField(default=0)  # simple like counter

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.replace('_', ' ').title()} post by {self.user.email} in {self.state.state_name}"


    

    

