from django import forms
from .models import OfertaPracy

class OfertaPracyForm(forms.ModelForm):
    class Meta:
        model = OfertaPracy
        fields = [
            'tytul',
            'branza',
            'zawod',
            'stanowisko',
            'opis',
            'lokalizacja',
            'wynagrodzenie',
            'data_wygasniecia',
            'status',
        ]
