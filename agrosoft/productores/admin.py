from django.contrib import admin
from .models import Productor, Cultivo
from .models import BoletinPrecios

admin.site.register(BoletinPrecios)
admin.site.register(Productor)
admin.site.register(Cultivo)