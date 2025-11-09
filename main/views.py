from django.shortcuts import render

def home(request):
    return render(request, "index.html")

def catalog(request):
    return render(request, "catalog.html")

def news(request):
    return render(request, "news.html")

def contacts(request):
    return render(request, "contacts.html")

def cart(request):
    return render(request, "cart.html")
