from django.contrib import admin

from .models import Hospital, AmbulanceAsset, AssetRequest, OperationHistory, HospitalOfficers

# Register your models here.
admin.site.register(Hospital)

admin.site.register(AmbulanceAsset)

admin.site.register(AssetRequest)

admin.site.register(OperationHistory)

admin.site.register(HospitalOfficers)