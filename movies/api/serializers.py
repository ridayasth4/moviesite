from rest_framework import serializers
from movies.models import Movie, Genre, Review


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class MovieListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    avg_rating_val = serializers.FloatField(read_only=True)

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


class MovieDetailSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    avg_rating_val = serializers.FloatField(read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'  # includes avg_rating_val automatically


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
