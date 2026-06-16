from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'zumex'

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy-policy/', TemplateView.as_view(template_name='zumex/privacy_policy.html'), name='privacy_policy'),
    path('terms-of-service/', TemplateView.as_view(template_name='zumex/terms_of_service.html'), name='terms_of_service'),
]
