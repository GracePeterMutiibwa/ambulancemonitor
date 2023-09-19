from django.db import models

# Create your models here.
class Hospital(models.Model):
    hospitalName = models.TextField(max_length=200, blank=False)

    hospitalUniqueId = models.UUIDField()

class AmbulanceAsset(models.Model):
    assetOwner = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="available_assets")

    assetCategory = models.TextField(max_length=200, blank=False)

    assetLicensePlate =  models.TextField(max_length=200, blank=False)

    assetSittingCapacity = models.IntegerField(blank=False)

    serviceStatus = models.BooleanField(blank=False)

    def __str__(self):
        return f"Hospital:{self.assetOwner.hospitalName}\nCategory:{self.assetCategory}\nCapacity:{self.assetSittingCapacity}"

class AssetRequest(models.Model):
    assetId = models.IntegerField(blank=False)

    assetOwner = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="incoming_requests")

    assetRequestor = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="sent_requests")

    requestStatus = models.BooleanField(blank=False)


    def getAssetLicencePlate(self, assetId):
        return AmbulanceAsset.objects.get(pk=assetId).assetLicensePlate

    def __str__(self):
        return self.getAssetLicencePlate(self.assetId)



class OperationHistory(models.Model):
    serviceDate = models.DateField(auto_now=True)

    requestingHospital = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="related_hospital")

    assetRequestedLicensePlate = models.TextField(max_length=200, blank=False)

    controlPersonnel = models.TextField(max_length=200, blank=False)

    requestTime = models.TimeField(auto_now=True)

    def __str__(self):
        # get the date
        date_object = f"{self.serviceDate.day}-{self.serviceDate.month}-{self.serviceDate.year}"

        time_object = "{}".format(self.requestTime.strftime("%H:%M:%S %p"))

        return f"{date_object} At {time_object}"



class HospitalOfficers(models.Model):
    employeeHospital = models.ForeignKey(Hospital, blank=False, on_delete=models.CASCADE, related_name="authenticatedPersonnel")

    employeeEmail = models.TextField(max_length=200)

    employeePassword = models.TextField(max_length=45)

    createdDate = models.DateField(auto_now=True)
