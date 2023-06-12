from django.contrib import admin
from .models import Movie, Participant, Interaction

# Register your models here.
admin.site.register(Movie)
admin.site.register(Participant)
admin.site.register(Interaction)