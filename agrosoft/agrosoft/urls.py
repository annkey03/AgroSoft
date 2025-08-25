from django.contrib import admin
from django.urls import path
from productores import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.recomendar_productos, name='inicio'),  # Página principal
    path('recomendar/', views.recomendar_productos, name='recomendar_productos'),
    path('api/precios/', views.api_precios_sipsa, name='api_precios_sipsa'),  # API endpoint
]
