from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('solicitar-recomendacion/', views.solicitar_recomendacion, name='solicitar_recomendacion'),
    path('', views.home, name='home'),
]