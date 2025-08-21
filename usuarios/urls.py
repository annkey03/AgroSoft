from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('solicitar-recomendacion/', views.solicitar_recomendacion, name='solicitar_recomendacion'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('cambiar-contrasena/<str:token>/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('', views.home, name='home'),
    path('productos/', views.products, name='productos'),
]
