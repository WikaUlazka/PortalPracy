from .forms import OfertaPracyForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ProfilPracodawcy, ProfilKandydata
from .models import Uzytkownik
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import make_password
import datetime

from django.contrib.auth.hashers import check_password

def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        haslo = request.POST.get('haslo')

        try:
            user = Uzytkownik.objects.get(email=email)
            if check_password(haslo, user.haslo):
                # Zaloguj użytkownika - np. zapisz w sesji:
                request.session['user_id'] = user.id
                request.session['user_typ'] = user.typ_uzytkownika
                return redirect('home')
            else:
                error = "Nieprawidłowe hasło."
        except Uzytkownik.DoesNotExist:
            error = "Nie ma takiego użytkownika."

    return render(request, 'myapp/login.html', {'error': error})

def logout_view(request):
    try:
        del request.session['user_id']
        del request.session['user_typ']
    except KeyError:
        pass
    return redirect('home')

def home(request):
    return render(request, 'myapp/home.html')


@login_required
def accounts(request):
    user = request.user

    # Spróbuj pobrać jeden z profili
    try:
        profil_kandydata = ProfilKandydata.objects.get(uzytkownik=user)
        return render(request, 'myapp/profil_kandydata.html', {'profil': profil_kandydata})
    except ProfilKandydata.DoesNotExist:
        pass

    try:
        profil_pracodawcy = ProfilPracodawcy.objects.get(uzytkownik=user)
        return render(request, 'myapp/profil_pracodawcy.html', {'profil': profil_pracodawcy})
    except ProfilPracodawcy.DoesNotExist:
        pass

    # Jeśli użytkownik nie ma żadnego profilu (nie powinno się zdarzyć)
    return render(request, 'myapp/brak_profilu.html')


@login_required
def dodaj_oferte(request):
    if request.method == 'POST':
        form = OfertaPracyForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            # Przypisz profil pracodawcy na podstawie zalogowanego użytkownika
            oferta.pracodawca = request.user.uzytkownik.profilpracodawcy
            oferta.data_dodania = datetime.date.today()
            if not oferta.status:
                oferta.status = 'aktywny'
            oferta.save()
            return redirect('home')  # lub inna strona po dodaniu
    else:
        form = OfertaPracyForm()
    return render(request, 'myapp/dodaj_oferte.html', {'form': form})

def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        imie = request.POST.get('imie')
        nazwisko = request.POST.get('nazwisko')

        if not username or not password1 or not password2 or not imie:
            error = "Wszystkie pola są wymagane."
        elif password1 != password2:
            error = "Hasła nie są takie same."
        elif Uzytkownik.objects.filter(email=username).exists():
            error = "Użytkownik o takim emailu już istnieje."
        else:
            user = Uzytkownik.objects.create(
                email=username,
                imie=imie,
                haslo=make_password(password1),
                # inne pola jeśli są wymagane
            )
            return redirect('home')

    return render(request, 'myapp/register.html', {'error': error})

def profile_kandydat_view(request, user_id):
    user = get_object_or_404(Uzytkownik, id=user_id)
    return render(request, 'myapp/profile_kandydat.html', {'user': user})

def profile_pracodawca_view(request, user_id):
    user = get_object_or_404(Uzytkownik, id=user_id)
    return render(request, 'myapp/profile_pracodawca.html', {'user': user})
