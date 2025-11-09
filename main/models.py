from django.contrib.auth.models import User
from django.db import models


class Service(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва послуги")
    description = models.TextField(verbose_name="Опис")
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Фото")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Послуга"
        verbose_name_plural = "Послуги"


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст новини")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Фото")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публікації")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новина"
        verbose_name_plural = "Новини"


class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва відділу або особи")
    phone = models.CharField(max_length=50, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=200, verbose_name="Адреса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакти"


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default="Рекламний ресурс", verbose_name="Назва сайту")
    logo = models.ImageField(upload_to='logo/', blank=True, null=True, verbose_name="Логотип")
    background = models.ImageField(upload_to='backgrounds/', blank=True, null=True, verbose_name="Фон (опціонально)")

    def __str__(self):
        return "Налаштування сайту"

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Користувач")
    title = models.CharField(max_length=200, verbose_name="Назва замовлення")
    description = models.TextField(verbose_name="Опис роботи")
    image = models.ImageField(upload_to='orders/', blank=True, null=True, verbose_name="Фото замовлення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"


class SupportChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_chat', verbose_name="Користувач")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Відправник")
    message = models.TextField(verbose_name="Повідомлення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    is_admin = models.BooleanField(default=False, verbose_name="Від адміністратора")

    def __str__(self):
        return f"Повідомлення від {self.sender.username} → {self.user.username}"

    class Meta:
        verbose_name = "Повідомлення чату"
        verbose_name_plural = "Чат підтримки"
        ordering = ['created_at']


class ServiceOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="service_orders", verbose_name="Користувач")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Послуга")
    description = models.TextField(verbose_name="Додаткова інформація", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата замовлення")
    status = models.CharField(max_length=50, default="Нове", verbose_name="Статус")

    def __str__(self):
        return f"{self.user.username} → {self.service.title}"

    class Meta:
        verbose_name = "Замовлення послуги"
        verbose_name_plural = "Замовлення послуг"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")

    def __str__(self):
        return self.user.username
