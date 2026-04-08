from rest_framework import serializers
from movies.models import Movie, Genre, Review

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class MovieListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    # Using a MethodField ensures we get the rating even if the view forgot to annotate it
    avg_rating_val = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id',
            'title',
            'poster',
            'release_date',
            'avg_rating_val',
            'genre',
        ]

    def get_avg_rating_val(self, obj):
        # Checks if annotated by view, otherwise falls back to model property/method
        return getattr(obj, 'avg_rating_val', obj.avg_rating or 0.0)

class MovieDetailSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    avg_rating_val = serializers.SerializerMethodField()
    # Adding reviews count or stars list to match your view logic
    stars_list = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = '__all__'

    def get_avg_rating_val(self, obj):
        return obj.avg_rating or 0.0

    def get_stars_list(self, obj):
        avg = obj.avg_rating or 0
        return [
            'full' if i <= avg else
            'half' if i - avg < 1 else
            'empty'
            for i in range(1, 6)
        ]

class ReviewSerializer(serializers.ModelSerializer):
    # 'user' is a ForeignKey, StringRelatedField shows the username
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']