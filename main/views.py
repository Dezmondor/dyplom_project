from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Service, News, Contact, Order, SupportChat, ServiceOrder, UserProfile
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Max, Q
from django.http import JsonResponse


# 🔒 Декоратор, який дозволяє доступ лише адміністраторам
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


@admin_required
def admin_support_list(request):
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

    return render(request, "admin_support_list.html", {"user_data": user_data, })


@admin_required
def get_unread_count(request):
    """Повертає кількість непрочитаних повідомлень для AJAX-запиту"""
    count = SupportChat.objects.filter(is_read=False).count()
    return JsonResponse({'count': count})


@admin_required
def admin_chat_view(request, user_id):
    target_user = User.objects.get(pk=user_id)
    chat_messages = SupportChat.objects.filter(user=target_user).order_by('created_at')
    SupportChat.objects.filter(is_read=False).update(is_read=True)

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

    })


def home(request):
    services = Service.objects.all()[:3]
    news = News.objects.order_by('-date')[:3]

    return render(request, "index.html", {"services": services, "news": news, })


def catalog(request):
    services = Service.objects.all()

    return render(request, "catalog.html", {"services": services, })


def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, "service_detail.html", {"service": service, })


def news_list(request):
    news = News.objects.all().order_by('-date')
    return render(request, "news.html", {"news": news, })


def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    return render(request, "news_detail.html", {"news": news_item})


def news(request):
    news_list = News.objects.order_by('-date')
    return render(request, "news.html", {"news_list": news_list})


def contacts(request):
    contact = Contact.objects.all()
    return render(request, "contacts.html", {"contacts": contact})


def cart(request):
    return render(request, "cart.html", {})


def register_view(request):
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
        UserProfile.objects.create(user=user, phone=phone)

        login(request, user)
        return redirect("profile")

    return render(request, "register.html")


def login_view(request):
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

    return render(request, "login.html")


@login_required
def profile_view(request):
    # 🔹 Якщо користувач — адміністратор, показуємо всі замовлення
    if request.user.is_staff:
        orders = ServiceOrder.objects.select_related('user', 'service').order_by('-created_at')
    else:
        orders = ServiceOrder.objects.filter(user=request.user).select_related('service').order_by('-created_at')

    chat_messages = SupportChat.objects.filter(user=request.user).order_by('created_at')

    # 🔹 Відправлення повідомлення у чат
    if request.method == "POST" and "message" in request.POST:
        text = request.POST.get("message", "").strip()
        if text:
            SupportChat.objects.create(
                user=request.user,
                sender=request.user,
                message=text,
                is_admin=request.user.is_staff
            )
            messages.success(request, "Повідомлення відправлено.")
        return redirect("profile")

    return render(request, "profile.html", {
        "orders": orders,
        "chat_messages": chat_messages,
    })


def logout_view(request):
    logout(request)
    return redirect("home")


def make_order(request):
    # 🔹 Якщо користувач не залогінений — показуємо сторінку з повідомленням
    if not request.user.is_authenticated:
        return render(request, "order_guest.html")

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

    return render(request, "order_service.html", {
        "services": services,
    })


@admin_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id)
    user = order.user

    return render(request, "admin_order_detail.html", {
        "order": order,
        "user_info": user,
    })


@login_required
def user_order_detail(request, order_id):
    order = get_object_or_404(ServiceOrder, id=order_id, user=request.user)
    return render(request, "user_order_detail.html", {"order": order})


@admin_required
def admin_user_list(request):
    users = User.objects.all().order_by('date_joined')
    return render(request, "admin_user_list.html", {"users": users})


@admin_required
def admin_user_detail(request, user_id):
    user_info = get_object_or_404(User, id=user_id)
    orders = ServiceOrder.objects.filter(user=user_info).select_related('service').order_by('-created_at')

    return render(request, "admin_user_detail.html", {
        "user_info": user_info,
        "orders": orders,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    services = []
    news = []

    if query:
        services = Service.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        news = News.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    context = {
        "query": query,
        "services": services,
        "news": news,
    }
    return render(request, "search_results.html", context)
