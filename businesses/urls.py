# businesses/urls.py
from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    # Business websites - this handles yourdomain.com/business-name/
    path('<slug:business_slug>/', views.business_website_view, name='website'),
    
    # Booking endpoints
    path('<slug:business_slug>/book/', views.create_booking, name='create_booking'),
]