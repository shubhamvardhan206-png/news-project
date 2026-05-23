from .models import Category

def common_data(request):
    return {
        'categories': Category.objects.all(),
    }