from django.urls import path
from . import views

urlpatterns = [
    # Client endpoints
    path('login', views.login),
    path('logout', views.logout),
    path('user_data', views.get_user_data),
    path('edit_client', views.edit_client),
    path('dass_test_results', views.dass_test_results),
    path('generate_signed_url', views.generate_signed_url),
    path('mark_notifications_read', views.mark_notifications_read),
    path('mark_all_notifications_hidden', views.mark_all_notifications_hidden),
    path('translations', views.translations),
    # CRM endpoints (staff)
    path('crm/login', views.crm_login),
    path('crm/dashboard', views.crm_dashboard),
    path('crm/client/<int:customer_id>/', views.crm_client_data),
]
