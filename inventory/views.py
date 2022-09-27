from django.shortcuts import render

def index(request):
    context = {
        "title": "Index Page"
    }
    return render(request, "inventory/index.html", context=context)
