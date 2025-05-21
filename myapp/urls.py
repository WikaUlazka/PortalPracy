from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', views.accounts, name='user_account'),
    path('register/', views.register_view, name='register'),
    path('dodaj-oferte/', views.dodaj_oferte, name='dodaj_oferte'),
    path('profile/kandydat/<int:user_id>/', views.profile_kandydat_view, name='profile_kandydat'),
    path('profile/pracodawca/<int:user_id>/', views.profile_pracodawca_view, name='profile_pracodawca'),

]
