from django import forms
from django.core.exceptions import ValidationError

from .models import Aplikacja
from .models import OfertaPracy
from .models import Uzytkownik, ProfilKandydata, ProfilPracodawcy


class UzytkownikForm(forms.ModelForm):
    class Meta:
        model = Uzytkownik
        fields = ['email', 'haslo', 'imie', 'nazwisko', 'typ_uzytkownika']


class ProfilKandydataForm(forms.ModelForm):
    class Meta:
        model = ProfilKandydata
        fields = ['telefon', 'lokalizacja', 'cv_sciezka']


class ProfilPracodawcyForm(forms.ModelForm):
    class Meta:
        model = ProfilPracodawcy
        fields = ['nazwa_firmy', 'strona_www']


class AplikacjaForm(forms.ModelForm):
    class Meta:
        model = Aplikacja
        fields = ['wiek', 'wyksztalcenie', 'miejsce_zamieszkania', 'staz']
        widgets = {
            'list_motywacyjny_sciezka': forms.TextInput(attrs={'class': 'form-control'}),
        }


class OfertaPracyForm(forms.ModelForm):
    class Meta:
        model = OfertaPracy
        exclude = ['pracodawca', 'data_dodania', 'status']


class RejestracjaUzytkownikaForm(forms.ModelForm):
    password1 = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Potwierdź hasło', widget=forms.PasswordInput)

    class Meta:
        model = Uzytkownik
        fields = ['email', 'imie', 'nazwisko']


def clean_password2(self):
    password1 = self.cleaned_data.get("password1")
    password2 = self.cleaned_data.get("password2")
    if password1 and password2 and password1 != password2:
        raise ValidationError("Hasła nie są identyczne.")
    return password2


def save(self, commit=True):
    user = super().save(commit=False)
    user.haslo = self.cleaned_data["password1"]  # Zahashujesz później w widoku
    if commit:
        user.save()
    return user


class MailForm(forms.Form):
    temat = forms.CharField(max_length=100, label='Temat')
    tresc = forms.CharField(widget=forms.Textarea, label='Treść wiadomości')


class OdpowiedzNaWymaganiaForm(forms.Form):
    def __init__(self, *args, wymagania=None, **kwargs):
        super().__init__(*args, **kwargs)
        if wymagania:
            for wymaganie in wymagania:
                self.fields[f'wymaganie_{wymaganie.id}'] = forms.ChoiceField(
                    label=wymaganie.tresc,
                    choices=[(True, 'Spełniam'), (False, 'Nie spełniam')],
                    widget=forms.RadioSelect
                )
