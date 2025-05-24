from django.db import models


class Uzytkownik(models.Model):
    TYPY = (
        ('kandydat', 'Kandydat'),
        ('pracodawca', 'Pracodawca'),
    )

    email = models.EmailField(unique=True)
    haslo = models.CharField(max_length=128)
    imie = models.CharField(max_length=100)
    nazwisko = models.CharField(max_length=100)
    typ_uzytkownika = models.CharField(max_length=20, choices=TYPY)

    def __str__(self):
        return f"{self.email} ({self.typ_uzytkownika})"


class ProfilKandydata(models.Model):
    uzytkownik = models.OneToOneField(Uzytkownik, on_delete=models.CASCADE)
    telefon = models.CharField(max_length=20)
    lokalizacja = models.CharField(max_length=100)
    cv_sciezka = models.CharField(max_length=255)

    def __str__(self):
        return f"Profil Kandydata: {self.uzytkownik}"


class ProfilPracodawcy(models.Model):
    uzytkownik = models.OneToOneField('Uzytkownik', on_delete=models.CASCADE)
    nazwa_firmy = models.CharField(max_length=100)
    strona_www = models.URLField(blank=True)
    opis = models.TextField()

    def __str__(self):
        return self.nazwa_firmy


class OfertaPracy(models.Model):
    STANOWISKA = [
        ('programista', 'Programista'),
        ('analityk', 'Analityk'),
        ('sprzedawca', 'Sprzedawca'),
    ]

    branza = models.CharField(max_length=100, default=None)
    stanowisko = models.CharField(max_length=50, choices=STANOWISKA, default=None)
    opis = models.TextField()
    lokalizacja = models.CharField(max_length=100, default=None)
    data_dodania = models.DateField(auto_now_add=True)
    data_wygasniecia = models.DateField()
    status = models.CharField(max_length=20, default='aktywny')
    pracodawca = models.ForeignKey(ProfilPracodawcy, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.stanowisko} - {self.branza}"


class Wymaganie(models.Model):
    oferta = models.ForeignKey(OfertaPracy, on_delete=models.CASCADE, related_name='wymagania')
    tresc = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.tresc} ({self.oferta})"


class OdpowiedzNaWymaganie(models.Model):
    wymaganie = models.ForeignKey(Wymaganie, on_delete=models.CASCADE)
    kandydat = models.ForeignKey(ProfilKandydata, on_delete=models.CASCADE)
    spelnia = models.BooleanField()


class Aplikacja(models.Model):
    kandydat = models.ForeignKey(ProfilKandydata, on_delete=models.CASCADE)
    oferta = models.ForeignKey(OfertaPracy, on_delete=models.CASCADE)
    data_aplikacji = models.DateField()
    status = models.CharField(max_length=50)
    list_motywacyjny_sciezka = models.CharField(max_length=255, blank=True)

    # Dodatkowe dane wymagane przez ofertę
    wiek = models.PositiveIntegerField(null=True, blank=True)
    wyksztalcenie = models.CharField(max_length=100, blank=True)
    miejsce_zamieszkania = models.CharField(max_length=100, blank=True)
    staz = models.PositiveIntegerField(null=True, blank=True)  # staż w latach

    def __str__(self):
        return f"Aplikacja {self.kandydat} → {self.oferta}"


class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)

    def __str__(self):
        return self.nazwa


class OfertaKategoria(models.Model):
    oferta = models.ForeignKey(OfertaPracy, on_delete=models.CASCADE)
    kategoria = models.ForeignKey(Kategoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.oferta} - {self.kategoria}"


class Wiadomosc(models.Model):
    nadawca = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='wiadomosci_wyslane')
    odbiorca = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='wiadomosci_odebrane')
    tresc = models.TextField()
    data_wyslania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wiadomość od {self.nadawca} do {self.odbiorca} ({self.data_wyslania})"
