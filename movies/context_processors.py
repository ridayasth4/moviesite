from .models import Genre

def navbar_genres(request):
    return {
        'navbar_genres': Genre.objects.all()
    }
