from django.contrib import admin

from strivers.models import Athlete, ActivityOverview, ActivityData

# Register your models here.
admin.site.register(Athlete)
admin.site.register(ActivityOverview)
admin.site.register(ActivityData)