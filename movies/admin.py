from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_date','featured')
    search_fields = ('title', 'genre')
    list_filter = ('genre', 'release_date', 'featured')
    list_editable = ('featured',)
