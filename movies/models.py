from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from datetime import date, timedelta

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    # ⭐ Average rating (read-only)
    @property
    def avg_rating(self):
        return self.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # ⭐ Stars display (read-only)
    @property
    def stars_display(self):
        avg = self.avg_rating
        stars = []
        for i in range(1, 6):
            if i <= avg:
                stars.append('full')
            elif i - avg < 1:
                stars.append('half')
            else:
                stars.append('empty')
        return stars

    # ⏱ Runtime display (read-only)
    @property
    def display_duration(self):
        if self.duration:
            h = self.duration // 60
            m = self.duration % 60
            return f"{h}h {m}m"
        return "N/A"

    # 🆕 New movie badge (read-only)
    @property
    def is_new(self):
        return self.release_date >= date.today() - timedelta(days=30)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}"


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1–5
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('movie', 'user')  # 1 review per user per movie
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating})"
