from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Uzytkownik
from .models import ProfilKandydata, ProfilPracodawcy
admin.site.register(Uzytkownik)
admin.site.register(ProfilKandydata)
admin.site.register(ProfilPracodawcy)