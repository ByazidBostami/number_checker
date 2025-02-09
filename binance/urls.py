from django.urls import path
from .views import dashboard, process_file, download_valid

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("process_file/", process_file, name="process_file"),
    path("download_valid/", download_valid, name="download_valid"),
]
