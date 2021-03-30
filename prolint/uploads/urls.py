from django.urls import path
from .views import UploadDataView

urlpatterns = [
    path('', UploadDataView.as_view(), name='upload'),
]
