from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from plantapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/<int:pk>/', views.plant_detail, name='plant_detail'),
    path('plants/<int:plant_id>/add/', views.add_user_plant, name='add_user_plant'),
    path('my-plants/', views.my_plants, name='my_plants'),
    path('register/', views.register, name='register'),
    path('plant-care/<int:user_plant_id>/', views.plant_care, name='plant_care'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('care-calendar/', views.care_calendar, name='care_calendar'),
    path('shop/', views.shopping, name='shopping'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='plantapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('plant-care/<int:user_plant_id>/', views.plant_care, name='plant_care'),
    
    path('', include('plantapp.urls')),  # 👈 Include plantapp's URLs here
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)