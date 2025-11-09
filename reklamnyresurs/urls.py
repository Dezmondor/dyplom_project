from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('catalog/', views.catalog, name="catalog"),
    path('news/', views.news, name="news"),
    path('contacts/', views.contacts, name="contacts"),
    path('cart/', views.cart, name="cart"),
]
