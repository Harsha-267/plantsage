from django.urls import path
from .views import upload_plant_image,PlantListView

urlpatterns = [
    path('upload/', upload_plant_image, name='plant_image_upload'),
    path('plants/', PlantListView.as_view(), name='plant_list'),
]
