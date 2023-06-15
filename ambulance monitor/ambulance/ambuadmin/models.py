from django.db import models

# Create your models here.
class Hospital(models.Model):
    hospitalName = models.TextField(max_length=200, blank=False)

class AmbulanceAsset(models.Model):
    assetOwner = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="available_assets")

    assetCategory = models.TextField(max_length=200, blank=False)

    assetLicensePlate =  models.TextField(max_length=200, blank=False)

    assetSittingCapacity = models.IntegerField(blank=False)

    serviceStatus = models.BooleanField(blank=False)

class AssetRequest(models.Model):
    assetId = models.IntegerField(blank=False)


class OperationHistory(models.Model):
    serviceDate = models.DateField(auto_now=True)

    requestingHospital = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="related_hospital")

    assetRequestedLicensePlate = models.TextField(max_length=200, blank=False)

    controlPersonnel = models.TextField(max_length=200, blank=False)

    requestTime = models.TimeField(auto_now=True)



class HospitalOfficers(models.Model):
    employeeHospital = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="authenticatedPersonnel")

    employeeEmail = models.TextField(max_length=200)

    employeePassword = models.TextField(max_length=45)

    createdDate = models.DateField(auto_now=True)
