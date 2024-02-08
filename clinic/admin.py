from django.contrib import admin
from .models import Client, Notification, TestResult, Translation, AdminUser, CustomerNote

admin.site.register(Client)
admin.site.register(Notification)
admin.site.register(TestResult)
admin.site.register(Translation)
admin.site.register(AdminUser)
admin.site.register(CustomerNote)
