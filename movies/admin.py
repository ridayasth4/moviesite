from django.contrib import admin
from .models import Movie, Genre  # <-- import Genre

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_date', 'featured')
    search_fields = ('title', 'genre__name')  # use __name for FK
    list_filter = ('genre', 'release_date', 'featured')
    list_editable = ('featured',)

# Register Genre so it shows up in admin
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
