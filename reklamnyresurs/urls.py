from django.contrib import admin
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('catalog/', views.catalog, name="catalog"),
    path('catalog/<int:service_id>/', views.service_detail, name='service_detail'),
    path('news/', views.news_list, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('search/', views.search, name='search'),
    path('contacts/', views.contacts, name="contacts"),
    path('cart/', views.cart, name="cart"),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-chat/<int:user_id>/', views.admin_chat_view, name='admin_chat'),
    path('admin-support/', views.admin_support_list, name='admin_support_list'),
    path('order/', views.make_order, name='make_order'),
    path('admin-order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('order-detail/<int:order_id>/', views.user_order_detail, name='user_order_detail'),
    path('admin-users/', views.admin_user_list, name='admin_user_list'),
    path('admin-user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
