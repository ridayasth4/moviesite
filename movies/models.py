from django.db import models

# Create your models here.
from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

