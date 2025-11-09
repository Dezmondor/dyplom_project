from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('catalog/', views.catalog, name="catalog"),
    path('catalog/<int:pk>/', views.service_detail, name="service_detail"),  # 🆕 новий маршрут
    path('news/', views.news, name="news"),
    path('contacts/', views.contacts, name="contacts"),
    path('cart/', views.cart, name="cart"),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-chat/<int:user_id>/', views.admin_chat_view, name='admin_chat'),
    path('admin-support/', views.admin_support_list, name='admin_support_list'),
    path('order/', views.make_order, name='make_order'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)