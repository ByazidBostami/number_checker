from django.contrib import admin
from django.urls import path, include
from binance import views  # Import views from the binance app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('binance/', include('binance.urls')),
    path('', views.dashboard, name='home'),  # Set the dashboard as the homepage
]
