from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Service, News, Contact, SiteSettings, Order, SupportChat, ServiceOrder
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max


# 🔒 Декоратор, який дозволяє доступ лише адміністраторам
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


@admin_required
def admin_support_list(request):
    site_settings = get_site_settings()

    # Отримуємо список користувачів, які писали у підтримку
    users_with_messages = (
        SupportChat.objects
        .values('user')
        .annotate(last_message=Max('created_at'))
        .order_by('-last_message')
    )

    # Отримуємо об’єкти користувачів
    user_data = []
    for entry in users_with_messages:
        u = User.objects.get(id=entry['user'])
        last_msg = SupportChat.objects.filter(user=u).order_by('-created_at').first()
        user_data.append({
            'user': u,
            'last_message': last_msg.message[:50] + ('...' if len(last_msg.message) > 50 else ''),
            'last_time': last_msg.created_at
        })

    return render(request, "admin_support_list.html", {"user_data": user_data, "site_settings": site_settings})


@admin_required
def admin_chat_view(request, user_id):
    site_settings = get_site_settings()

    target_user = User.objects.get(pk=user_id)
    chat_messages = SupportChat.objects.filter(user=target_user).order_by('created_at')

    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            SupportChat.objects.create(
                user=target_user,
                sender=request.user,
                message=text,
                is_admin=True
            )
        return redirect("admin_chat", user_id=user_id)

    return render(request, "admin_chat.html", {
        "target_user": target_user,
        "chat_messages": chat_messages,
        "site_settings": site_settings
    })


def get_site_settings():
    settings = SiteSettings.objects.first()
    return settings


def home(request):
    services = Service.objects.all()[:3]
    news = News.objects.order_by('-date')[:3]
    site_settings = get_site_settings()
    return render(request, "index.html", {"services": services, "news": news, "site_settings": site_settings})


def catalog(request):
    services = Service.objects.all()
    site_settings = get_site_settings()
    return render(request, "catalog.html", {"services": services, "site_settings": site_settings})


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    site_settings = get_site_settings()
    return render(request, "service_detail.html", {"service": service, "site_settings": site_settings})


def news(request):
    news_list = News.objects.order_by('-date')
    site_settings = get_site_settings()
    return render(request, "news.html", {"news_list": news_list, "site_settings": site_settings})


def contacts(request):
    contact = Contact.objects.all()
    site_settings = get_site_settings()
    return render(request, "contacts.html", {"contacts": contact, "site_settings": site_settings})


def cart(request):
    site_settings = get_site_settings()
    return render(request, "cart.html", {"site_settings": site_settings})


def register_view(request):
    site_settings = get_site_settings()
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = email.split("@")[0]
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Паролі не співпадають!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Користувач із таким email вже існує.")
            return redirect("register")

        # 🧍‍♂️ Створюємо користувача з ім'ям і прізвищем
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        login(request, user)
        return redirect("profile")

    return render(request, "register.html", {"site_settings": site_settings})


def login_view(request):
    site_settings = get_site_settings()
    if request.method == "POST":
        email = request.POST.get("email")
        username = email.split("@")[0]
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("profile")
        else:
            messages.error(request, "Невірний логін або пароль.")
            return redirect("login")

    return render(request, "login.html", {"site_settings": site_settings})


@login_required
def profile_view(request):
    site_settings = get_site_settings()

    orders = Order.objects.filter(user=request.user)
    chat_messages = SupportChat.objects.filter(user=request.user).order_by('created_at')

    # 🔹 Якщо користувач надсилає повідомлення
    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            SupportChat.objects.create(
                user=request.user,
                sender=request.user,
                message=text,
                is_admin=False
            )
            messages.success(request, "Повідомлення надіслано службі підтримки.")
        return redirect("profile")

    # 🔹 Якщо просто GET-запит — відображаємо сторінку
    return render(request, "profile.html", {
        "orders": orders,
        "chat_messages": chat_messages,
        "site_settings": site_settings
    })


def logout_view(request):
    logout(request)
    return redirect("home")


def make_order(request):
    site_settings = get_site_settings()

    # 🔹 Якщо користувач не залогінений — показуємо сторінку з повідомленням
    if not request.user.is_authenticated:
        return render(request, "order_guest.html", {"site_settings": site_settings})

    services = Service.objects.all()

    if request.method == "POST":
        service_id = request.POST.get("service_id")
        description = request.POST.get("description")
        service = Service.objects.get(id=service_id)

        ServiceOrder.objects.create(
            user=request.user,
            service=service,
            description=description
        )
        messages.success(request, "Ваше замовлення успішно відправлено!")
        return redirect("profile")

    return render(request, "order_service.html", {"services": services, "site_settings": site_settings})