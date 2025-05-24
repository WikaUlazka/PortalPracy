import datetime

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .forms import (
    OfertaPracyForm,
    RejestracjaUzytkownikaForm,
    ProfilKandydataForm,
    ProfilPracodawcyForm,
    MailForm,
    AplikacjaForm,
    OdpowiedzNaWymaganiaForm
)
from .models import (
    Uzytkownik,
    ProfilPracodawcy,
    Aplikacja,
    OfertaPracy,
    ProfilKandydata,
    OdpowiedzNaWymaganie,
    Wymaganie
)


def lista_ofert(request):
    oferty = OfertaPracy.objects.filter(status='aktywny', data_wygasniecia__gte=timezone.now())
    return render(request, 'myapp/oferty/moje_oferty.html', {'oferty': oferty})


def szczegoly_oferty(request, oferta_id):
    oferta = get_object_or_404(OfertaPracy, id=oferta_id)
    aplikacje = None
    uzytkownik = None
    total_aplikacji = 0
    spelnia_wszystkie = 0
    niespelnia_wszystkich = 0

    uzytkownik_id = request.session.get("uzytkownik_id")
    if uzytkownik_id:
        try:
            uzytkownik = Uzytkownik.objects.get(id=uzytkownik_id)
            if uzytkownik.typ_uzytkownika == "pracodawca" and oferta.pracodawca.uzytkownik_id == uzytkownik.id:
                aplikacje = Aplikacja.objects.filter(oferta=oferta).select_related('kandydat__uzytkownik')
                wymagania = Wymaganie.objects.filter(oferta=oferta)
                total_aplikacji = aplikacje.count()

                for aplikacja in aplikacje:
                    odpowiedzi = OdpowiedzNaWymaganie.objects.filter(
                        wymaganie__in=wymagania,
                        kandydat=aplikacja.kandydat
                    )
                    if wymagania.exists() and odpowiedzi.filter(spelnia=False).exists():
                        niespelnia_wszystkich += 1
                    elif wymagania.exists():
                        spelnia_wszystkie += 1

        except Uzytkownik.DoesNotExist:
            pass

    return render(request, 'myapp/oferty/szczegoly.html', {
        'oferta': oferta,
        'uzytkownik': uzytkownik,
        'aplikacje': aplikacje,
        'total_aplikacji': total_aplikacji,
        'spelnia_wszystkie': spelnia_wszystkie,
        'niespelnia_wszystkich': niespelnia_wszystkich,
    })


def aplikuj(request, oferta_id):
    uzytkownik_id = request.session.get('uzytkownik_id')
    if not uzytkownik_id:
        return redirect('login')

    uzytkownik = get_object_or_404(Uzytkownik, id=uzytkownik_id)
    oferta = get_object_or_404(OfertaPracy, id=oferta_id)

    try:
        kandydat = ProfilKandydata.objects.get(uzytkownik=uzytkownik)
    except ProfilKandydata.DoesNotExist:
        return redirect('home')

    wymagania = oferta.wymagania.all()  # <-- wymagania z tej oferty

    if request.method == 'POST':
        form = AplikacjaForm(request.POST)
        form_wymagania = OdpowiedzNaWymaganiaForm(request.POST, wymagania=wymagania)
        if form.is_valid() and form_wymagania.is_valid():
            aplikacja = form.save(commit=False)
            aplikacja.kandydat = kandydat
            aplikacja.oferta = oferta
            aplikacja.data_aplikacji = timezone.now()
            aplikacja.status = 'Wysłana'
            aplikacja.save()

            # Zapisz odpowiedzi na wymagania
            for wymaganie in wymagania:
                odpowiedz = form_wymagania.cleaned_data[f'wymaganie_{wymaganie.id}'] == 'True'
                OdpowiedzNaWymaganie.objects.create(
                    wymaganie=wymaganie,
                    kandydat=kandydat,
                    spelnia=odpowiedz
                )

            return redirect('moje_aplikacje')
    else:
        form = AplikacjaForm()
        form_wymagania = OdpowiedzNaWymaganiaForm(wymagania=wymagania)

    return render(request, 'myapp/oferty/aplikuj.html', {
        'form': form,
        'form_wymagania': form_wymagania,
        'oferta': oferta,
        'wymagania': wymagania,
    })


def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        haslo = request.POST['haslo']
        try:
            user = Uzytkownik.objects.get(email=email)
            if check_password(haslo, user.haslo):
                request.session['uzytkownik_id'] = user.id

                if user.typ_uzytkownika == 'kandydat':
                    return redirect('profile_kandydat', user_id=user.id)
                elif user.typ_uzytkownika == 'pracodawca':
                    return redirect('profile_pracodawca', user_id=user.id)
                else:
                    return redirect('home')  # fallback
            else:
                raise Uzytkownik.DoesNotExist
        except Uzytkownik.DoesNotExist:
            return render(request, 'myapp/oferty/login.html', {'error': 'Nieprawidłowe dane logowania'})
    return render(request, 'myapp/oferty/login.html')


def logout_user(request):
    request.session.flush()
    return redirect('home')


def home(request):
    oferty = OfertaPracy.objects.filter(
        status='aktywny',
        data_wygasniecia__gte=timezone.now()
    )

    query = request.GET.get('q')
    lokalizacja = request.GET.get('lokalizacja')

    if query:
        oferty = oferty.filter(
            Q(stanowisko__icontains=query) |
            Q(branza__icontains=query) |
            Q(opis__icontains=query)
        )
    if lokalizacja:
        oferty = oferty.filter(lokalizacja__icontains=lokalizacja)

    uzytkownik = None
    uzytkownik_id = request.session.get('uzytkownik_id')
    if uzytkownik_id:
        try:
            uzytkownik = Uzytkownik.objects.get(id=uzytkownik_id)
        except Uzytkownik.DoesNotExist:
            pass

    return render(request, 'myapp/home.html', {
        'oferty': oferty,
        'uzytkownik': uzytkownik
    })


def accounts(request):
    uzytkownik_id = request.session.get('uzytkownik_id')
    if not uzytkownik_id:
        return redirect('login')

    uzytkownik = Uzytkownik.objects.get(id=uzytkownik_id)

    try:
        profil_kandydata = ProfilKandydata.objects.get(uzytkownik=uzytkownik)
        return render(request, 'myapp/oferty/profil_kandydata.html', {'profil': profil_kandydata})
    except ProfilKandydata.DoesNotExist:
        pass

    try:
        profil_pracodawcy = ProfilPracodawcy.objects.get(uzytkownik=uzytkownik)
        return render(request, 'myapp/oferty/profil_pracodawcy.html', {'profil': profil_pracodawcy})
    except ProfilPracodawcy.DoesNotExist:
        pass

    return render(request, 'myapp/brak_profilu.html')


def dodaj_oferte(request):
    uzytkownik_id = request.session.get('uzytkownik_id')
    if not uzytkownik_id:
        return redirect('login')

    try:
        uzytkownik = Uzytkownik.objects.get(id=uzytkownik_id)
        profil = ProfilPracodawcy.objects.get(uzytkownik=uzytkownik)
    except (Uzytkownik.DoesNotExist, ProfilPracodawcy.DoesNotExist):
        return redirect('login')

    if request.method == 'POST':
        form = OfertaPracyForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.pracodawca = profil
            oferta.data_dodania = datetime.date.today()
            if not oferta.status:
                oferta.status = 'aktywny'
            oferta.save()

            # 🔽 DODANE: zapisanie dynamicznych wymagań
            wymagania_lista = request.POST.getlist('wymagania')
            for tresc in wymagania_lista:
                if tresc.strip():
                    Wymaganie.objects.create(oferta=oferta, tresc=tresc.strip())

            return redirect('szczegoly_oferty', oferta_id=oferta.id)
    else:
        form = OfertaPracyForm()

    return render(request, 'myapp/oferty/dodaj_oferte.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form_uzytkownik = RejestracjaUzytkownikaForm(request.POST)
        typ = request.POST.get('typ_uzytkownika')

        if typ == 'kandydat':
            form_profil_kandydata = ProfilKandydataForm(request.POST)
            form_profil_pracodawcy = ProfilPracodawcyForm()
        elif typ == 'pracodawca':
            form_profil_pracodawcy = ProfilPracodawcyForm(request.POST)
            form_profil_kandydata = ProfilKandydataForm()
        else:
            return render(request, 'myapp/oferty/register.html', {
                'form_uzytkownik': form_uzytkownik,
                'form_profil_kandydata': ProfilKandydataForm(),
                'form_profil_pracodawcy': ProfilPracodawcyForm(),
                'error': 'Niepoprawny typ użytkownika'
            })

        aktywny_form_profilu = form_profil_kandydata if typ == 'kandydat' else form_profil_pracodawcy

        if form_uzytkownik.is_valid() and aktywny_form_profilu.is_valid():
            uzytkownik = form_uzytkownik.save(commit=False)
            uzytkownik.haslo = make_password(form_uzytkownik.cleaned_data['password1'])
            uzytkownik.typ_uzytkownika = typ
            uzytkownik.save()

            profil = aktywny_form_profilu.save(commit=False)
            profil.uzytkownik = uzytkownik
            profil.save()

            return redirect('login')  # ✅ poprawnie przekierowujemy po rejestracji

    else:
        form_uzytkownik = RejestracjaUzytkownikaForm()
        form_profil_kandydata = ProfilKandydataForm()
        form_profil_pracodawcy = ProfilPracodawcyForm()

    return render(request, 'myapp/oferty/register.html', {
        'form_uzytkownik': form_uzytkownik,
        'form_profil_kandydata': form_profil_kandydata,
        'form_profil_pracodawcy': form_profil_pracodawcy,
    })


def profile_kandydat_view(request, user_id):
    user = get_object_or_404(Uzytkownik, id=user_id)
    return render(request, 'myapp/oferty/profil_kandydata.html', {'user': user})


def profile_pracodawca_view(request, user_id):
    user = get_object_or_404(Uzytkownik, id=user_id)
    return render(request, 'myapp/oferty/profil_pracodawcy.html', {'user': user})


def moje_aplikacje(request):
    uzytkownik_id = request.session.get('uzytkownik_id')
    if not uzytkownik_id:
        return redirect('login')

    uzytkownik = Uzytkownik.objects.get(id=uzytkownik_id)
    if uzytkownik.typ_uzytkownika != 'kandydat':
        return redirect('login')

    profil = ProfilKandydata.objects.get(uzytkownik=uzytkownik)
    aplikacje = Aplikacja.objects.filter(kandydat=profil)
    return render(request, 'myapp/oferty/moje_aplikacje.html', {'aplikacje': aplikacje})


def moje_oferty(request):
    uzytkownik_id = request.session.get('uzytkownik_id')
    if not uzytkownik_id:
        return redirect('login')

    uzytkownik = Uzytkownik.objects.get(id=uzytkownik_id)
    if uzytkownik.typ_uzytkownika != 'pracodawca':
        return redirect('login')

    profil = ProfilPracodawcy.objects.get(uzytkownik=uzytkownik)
    oferty = OfertaPracy.objects.filter(pracodawca=profil)

    # Dodaj liczbę aplikacji do każdej oferty
    for oferta in oferty:
        oferta.liczba_aplikacji = Aplikacja.objects.filter(oferta=oferta).count()

    return render(request, 'myapp/oferty/moje_oferty.html', {'oferty': oferty})


def zmien_status_aplikacji(request, aplikacja_id):
    aplikacja = get_object_or_404(Aplikacja, id=aplikacja_id)
    nowy_status = request.POST.get('nowy_status')
    if nowy_status in ['Zaakceptowana', 'Odrzucona']:
        aplikacja.status = nowy_status
        aplikacja.save()
    return redirect('szczegoly_oferty', oferta_id=aplikacja.oferta.id)


def wyslij_mail(request, aplikacja_id):
    uzytkownik_id = request.session.get('uzytkownik_id')
    if not uzytkownik_id:
        return redirect('login')

    aplikacja = get_object_or_404(Aplikacja, id=aplikacja_id)

    user = get_object_or_404(Uzytkownik, id=uzytkownik_id)
    if request.method == 'POST':
        form = MailForm(request.POST)
        if form.is_valid():
            temat = form.cleaned_data['temat']
            tresc = form.cleaned_data['tresc']
            email = EmailMessage(
                subject=temat,
                body=tresc,
                from_email=user.email,
                to=[aplikacja.kandydat.uzytkownik.email],
                reply_to=[user.email],
            )
            email.send()
            return redirect('szczegoly_oferty', oferta_id=aplikacja.oferta.id)
    else:
        form = MailForm()

    return render(request, 'myapp/wyslij_mail.html', {
        'form': form,
        'aplikacja': aplikacja,
        'pracodawca_email': user.email,
    })
