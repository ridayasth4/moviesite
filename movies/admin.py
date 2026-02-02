from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import Movie, Genre


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'genre',
        'release_date',
        'featured',
        'has_video',
    )
    search_fields = ('title', 'genre__name')
    list_filter = ('genre', 'release_date', 'featured')
    list_editable = ('featured',)
    readonly_fields = ('video_preview',)

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'title',
                'description',
                'genre',
                'release_date',
                'duration',
                'featured',
            )
        }),
        ('Media', {
            'fields': (
                'poster',
                'video',
                'video_url',
                'video_preview',
            )
        }),
    )

    def has_video(self, obj):
        return bool(obj.video or obj.video_url)
    has_video.boolean = True
    has_video.short_description = 'Video'

    def video_preview(self, obj):
        if obj.video:
            return format_html(
                '<video width="320" controls>'
                '<source src="{}" type="video/mp4">'
                'Your browser does not support the video tag.'
                '</video>',
                obj.video.url
            )
        elif obj.video_url:
            return format_html(
                '<a href="{}" target="_blank">Open Video</a>',
                obj.video_url
            )
        return "No video available"

    video_preview.short_description = "Video Preview"

    def save_model(self, request, obj, form, change):
        if obj.video and obj.video_url:
            raise ValidationError(
                "Please provide either a video file OR a video URL — not both."
            )
        super().save_model(request, obj, form, change)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
