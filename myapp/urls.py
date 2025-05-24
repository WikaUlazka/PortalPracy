from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('accounts/', views.accounts, name='user_account'),
    path('register/', views.register, name='register'),
    path('dodaj-oferte/', views.dodaj_oferte, name='dodaj_oferte'),
    path('profile/kandydat/<int:user_id>/', views.profile_kandydat_view, name='profile_kandydat'),
    path('profile/pracodawca/<int:user_id>/', views.profile_pracodawca_view, name='profile_pracodawca'),
    path('', views.lista_ofert, name='lista_ofert'),
    path('oferta/<int:oferta_id>/', views.szczegoly_oferty, name='szczegoly_oferty'),
    path('oferta/<int:oferta_id>/aplikuj/', views.aplikuj, name='aplikuj'),
    path('moje-aplikacje/', views.moje_aplikacje, name='moje_aplikacje'),
    path('moje-oferty/', views.moje_oferty, name='moje_oferty'),
    path('aplikacja/<int:aplikacja_id>/status/', views.zmien_status_aplikacji, name='zmien_status_aplikacji'),
    path('wyslij-mail/<int:aplikacja_id>/', views.wyslij_mail, name='wyslij_mail'),
]
