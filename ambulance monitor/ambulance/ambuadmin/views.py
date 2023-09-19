from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Hospital, HospitalOfficers, AmbulanceAsset, AssetRequest, OperationHistory
from django.http import JsonResponse
import uuid



def determineUserValidity(**userCredentials):
    # extract the entered details
    userEmail = userCredentials['email'][0]

    userPassword = userCredentials['password'][0]

    # get the user object
    userInstance = User.objects.filter(email=userEmail).first()

    if userInstance:
        # confirm the passwords
        if userInstance.check_password(userPassword) is True:
            return True, userInstance
        
        else:
            return True, False


    else:
        return False, None

# Create your views here.
def loginView(request):
    if request.method == "POST":
        # login details
        submittedLoginDetails = request.POST

        # get the details sent along
        validityCheckResults, userObject = determineUserValidity(**submittedLoginDetails)

        if validityCheckResults is True and userObject:
            # if its a valid user redirect them to home page after login
            login(request, userObject)

            # print("User Logged in:", userObject.username)

            return redirect("homepage")


        else:
            # password or email is wrong
            # print("Its wrong")
            pass

    elif request.user.is_authenticated:
        return redirect("homepage")

    return render(request, "ambuadmin/adminlogin.html")

def getHospitalsMeta():
    # get the hospitals
    presentHospitals = Hospital.objects.all()

    # store the details
    hospitalsMeta = []

    for eachHospital in presentHospitals:
        # get the id, name, assets, user count, operations
        referenceId = eachHospital.id

        hospitalName = eachHospital.hospitalName

        assetCount = len(eachHospital.available_assets.all())

        userCount = len(eachHospital.authenticatedPersonnel.all())

        operationCount = len(eachHospital.related_hospital.all())

        # store the details in a smaller object
        miniMeta = {
            'id': referenceId,
            'name': hospitalName,
            'assets': assetCount,
            'users': userCount,
            'operations': operationCount
        }

        # collect them
        hospitalsMeta.append(miniMeta)

    
    return hospitalsMeta





@login_required(login_url="loginpage")
def homeView(request):
    # get present hospital details
    hospitalsDetail = getHospitalsMeta()

    # prepare a context
    context = {
        'hospitals': hospitalsDetail
    }

    return render(request, "ambuadmin/index.html", context=context)

@login_required(login_url="loginpage")
def userManagementView(request):
    # get list of all hospitals
    hospitalList = [
        {
        'name': hospitalObject.hospitalName,
        'id': hospitalObject.id
        } for hospitalObject in Hospital.objects.all()]
    
    # get the list of present users
    usersList = [
        {
            'id': userObject.id,
            'email': userObject.employeeEmail,
            'hospital': userObject.employeeHospital.hospitalName,
            'date': userObject.createdDate
        } for userObject in HospitalOfficers.objects.all()
    ]

    # print("listia:", usersList)

    # prepare

    nameContext = {
        'hospitals': hospitalList,
        'users': usersList
    }

    return render(request, "ambuadmin/user-control.html", context=nameContext)


@login_required(login_url="loginpage")
def fleetHistoryView(request):
    # get  history data
    historyData = getAvailableHistory()

    return render(request, "ambuadmin/fleet-history.html", context=dict(
        history = historyData
    ))



def getAvailableHistory():
    # get the history present
    allHistory = OperationHistory.objects.all()

    historyOBjects = [
        dict(
            service_date = eachHistoryObject.serviceDate,
            requestor = eachHistoryObject.requestingHospital.hospitalName,
            license = eachHistoryObject.assetRequestedLicensePlate,
            personnel_email = eachHistoryObject.controlPersonnel,
            request_time = eachHistoryObject.requestTime.strftime("%H:%M %p")
        
        ) for eachHistoryObject in allHistory
    ]

    return historyOBjects


def checkHospitalValidity(nameOfHospital):
    # get all hospital names
    checkList = Hospital.objects.filter(hospitalName=nameOfHospital).first()


    presenceStatus = False if checkList else True

    return presenceStatus



@login_required(login_url="loginpage")
def registerHospital(request):
    # get the submitted info
    submittedName = request.POST.get("hospital-name")

    # get the status
    isValid = checkHospitalValidity(submittedName)

    # print("Duplicate Status:", isValid)

    if isValid is True:
        # record the hospital name
        # get a new id
        uniqueId = uuid.uuid4()

        hospitalObject = Hospital(
            hospitalName=submittedName,
            hospitalUniqueId=uniqueId
            )

        # save the object
        hospitalObject.save()



    else:
        # its a duplicate
        pass

    return redirect("homepage")

@login_required(login_url="loginpage")
def logoutUserView(request):
    # logout the user from the system
    logout(request)

    return redirect("loginpage")

@login_required(login_url="loginpage")
def deleteHospitalView(request, hospitalId):
    # delete the hospital
    hospitalToDelete = Hospital.objects.get(pk=hospitalId)

    # delete it from the database
    hospitalToDelete.delete()

    return redirect("homepage")

def checkUserValidity(userEmailAddress):
    # get all hospital names
    checkList = HospitalOfficers.objects.filter(employeeEmail=userEmailAddress).first()

    # print("List:", checkList)

    presenceStatus = False if checkList else True

    # print("Found Status:", presenceStatus)

    return presenceStatus


@login_required(login_url="loginpage")
def registerSystemAccessors(request):
    # get the details
    hospitalId = request.POST.get("hospital-id")

    userEmail = request.POST.get("user-email")

    userPassword = request.POST.get("user-key")

    # get the status
    userStatus = checkUserValidity(userEmail)

    if userStatus is True:
        # get an hospital object
        hospitalInstance = Hospital.objects.get(pk=hospitalId)

        # create and instance of the user
        hospitalIncharge = HospitalOfficers(
            employeeHospital=hospitalInstance,
            employeeEmail=userEmail,
            employeePassword=userPassword
            )
        
        # save the object
        hospitalIncharge.save()

        # print("Saved the incharge")

    else:
        # pass
        pass

    return redirect("userpage")


@login_required(login_url="loginpage")
def deleteInterfaceUser(request, userId):
    # delete the user
    userToDelete = HospitalOfficers.objects.get(pk=userId)

    # delete the user from the database
    userToDelete.delete()

    return redirect("userpage")


def validateHandShakeUser(requestingEmail, requestingPassword):
    # get user details
    userObject = HospitalOfficers.objects.filter(employeeEmail=requestingEmail).first()

    # determine if user is legitimate
    if userObject and userObject.employeePassword == requestingPassword:
        return True, (userObject.employeeHospital.id, userObject.employeeHospital.hospitalName, userObject.employeeHospital.hospitalUniqueId, userObject.employeeHospital)
    
    else:
        return False, None


def getAvailableAssets(idToIgnore):
    # get the owner hospital
    ownerHospital = Hospital.objects.get(pk=idToIgnore)

    # get
    assets = AmbulanceAsset.objects.filter(serviceStatus=False)

    # idle
    idleAssets = []

    # filter
    for eachAsset in assets:
        if (eachAsset.assetOwner != ownerHospital):
            # store the details
            idleAssets.append({
                eachAsset.assetLicensePlate: (
                                                eachAsset.assetOwner.hospitalName,
                                                eachAsset.assetCategory,
                                                eachAsset.assetSittingCapacity,
                                                eachAsset.pk
                                            )
            })
    
    return idleAssets


def getListOfRequests(hospitalObject, requestStatus):
    # get pending requets
    pendingRequests = hospitalObject.sent_requests.filter(requestStatus=requestStatus)

    return [(requestObject.assetId, str(requestObject)) for requestObject in pendingRequests if requestObject.requestStatus is True]

def getListOfIncomingRequests(hospitalObject):
    # get the requests
    incomingRequests = hospitalObject.incoming_requests.all()

    return {str(requestObject): requestObject.assetId for requestObject in incomingRequests if requestObject.requestStatus is False}

def getListOfLentRequests(hospitalObject):
    # get the requests
    incomingRequests = hospitalObject.incoming_requests.all()

    return {str(requestObject): requestObject.assetId for requestObject in incomingRequests if requestObject.requestStatus is True}

def getListOfAcceptedRequests(hospitalObject):
    # get the requests
    acceptedRequests = hospitalObject.sent_requests.all()

    return {str(requestObject): requestObject.assetId for requestObject in acceptedRequests if requestObject.requestStatus is True}


def getAssetDetail(request):
    # get the id of the selected asset
    assetId = request.GET.get('asset-id')

    requestType = request.GET.get('type')

    # get the asset
    assetToView = AmbulanceAsset.objects.get(pk=assetId)
    
    if requestType == 'normal':
        return JsonResponse(dict(
            message = str(assetToView)
        ))
    
    else:
        # get the asset request for that asset
        requestInstance = AssetRequest.objects.get(assetId=assetId)

        # get the assset itself
        requestedAsset = AmbulanceAsset.objects.get(pk=assetId)

        return JsonResponse(dict(
            message = f"Requestor:{requestInstance.assetRequestor.hospitalName}\nAsset Category:{requestedAsset.assetCategory}\nAsset Name:{requestedAsset.assetLicensePlate}\nAsset Capacity:{requestedAsset.assetSittingCapacity}"
        ))
    

def getListOfDeletableAssets(hospitalObject):
    # reference
    referenceList = []

    all_free_assets = hospitalObject.available_assets.filter(serviceStatus=False)

    for eachAsset in all_free_assets:
            # record the license plate
        referenceList.append(
                (
                    eachAsset.assetLicensePlate,
                    eachAsset.id,
                    eachAsset.assetOwner.hospitalUniqueId
                )
            )
    return referenceList



def provisionRequestedAsset(request):
    # get the id and the response
    assetId = request.GET.get('asset-id')

    requestReply = request.GET.get('reply')

    # update the asset and request data
    ownerHospital = updateAssetRequestData(assetId, requestReply)

    # get the updated list
    updatedIncomingLists = getListOfIncomingRequests(ownerHospital)

    # get a list of lent out assets
    lentAssets = getListOfLentRequests(ownerHospital)

    # get free assets
    own_free_assets = getListOfDeletableAssets(ownerHospital)

    return JsonResponse(dict(
        updated = updatedIncomingLists,
        lent = lentAssets,
        own = own_free_assets
    ))


def updateAssetRequestData(assetId, requestReply):
    # get the asset request
    requestInstance = AssetRequest.objects.get(assetId=assetId)

    # delete the request if the reply is no
    if requestReply is False:
        # delete the request
        requestInstance.delete()

    else:
        # update the status
        requestInstance.requestStatus = requestReply

        # update the status
        requestInstance.save()

    # get the assset itself
    requestedAsset = AmbulanceAsset.objects.get(pk=assetId)

    # update the response / reply
    requestedAsset.serviceStatus = requestReply

    # save the state of the object
    requestedAsset.save()

    # get the object of the owner hospital
    return requestedAsset.assetOwner


def makeAssetAvailable(assetId):
    # get the ambulance
    requestedAsset = AmbulanceAsset.objects.get(pk=assetId)

    # nake the asset avilable
    requestedAsset.serviceStatus = False

    # save the new provile
    requestedAsset.save()

    return requestedAsset.assetOwner

def releaseAmbulanceAsset(request):
    # get the id and the incharge
    assetId = request.GET.get('asset-id')

    inchargePersonell = request.GET.get('incharge')

    # get the hospital
    assetRequestInstance =  AssetRequest.objects.get(assetId=assetId)

    # get the requestor
    assetRequestor = assetRequestInstance.assetRequestor

    # get the license plate
    assetLicensePlate = str(assetRequestInstance)

    # create an instance of history
    historyRecord = OperationHistory(
        requestingHospital=assetRequestor,
        assetRequestedLicensePlate=assetLicensePlate,
        controlPersonnel=inchargePersonell
        )

    # save the history record
    historyRecord.save()

    # approve
    hospitalObject = makeAssetAvailable(assetId=assetId)

    # after clear the request
    assetRequestInstance.delete()

    # update the list
    newAcceptedList = getListOfAcceptedRequests(hospitalObject)

    # get update list of present assets
    idleAssets = getAvailableAssets(assetRequestor.pk)

    # return the updated list
    return JsonResponse(dict(
        updated = newAcceptedList,
        idle = idleAssets
    ))



def createHistoryDetail(historyObject):
    # contruct a display string
    displayString = "On {date_object}\n--------------------------------\nRequestor:{hospital}\nLicense Plate:{plate}\nIncharge:{incharge}".format_map(
        dict(
            date_object=str(historyObject),
            hospital=historyObject.requestingHospital.hospitalName,
            plate=historyObject.assetRequestedLicensePlate,
            incharge=historyObject.controlPersonnel
            )
        )
    
    return displayString

def getOperationHistory(historyOwner, filterObject=None):
    # get the 
    historyObjects = historyOwner.related_hospital.filter(serviceDate=filterObject) if filterObject else historyOwner.related_hospital.all()

    # create related view data items
    # 12-24-2023 At 12:36:PM : (1, 2)
    historyData = {
            str(eachHistoryObject): (eachHistoryObject.pk, eachHistoryObject.serviceDate.strftime('%d-%m-%Y'))

        for eachHistoryObject in historyObjects} 
    

    return historyData

def fetchHistoryDetail(request):
    # get the data to use
    historyId = request.GET.get('record-id')

    # get the history object
    historyObject = OperationHistory.objects.get(pk=historyId)

    # get the attached details
    attachedDetails = createHistoryDetail(historyObject)

    return JsonResponse(
        dict(
            details = attachedDetails
            )
    )

def manageHandShake(request):
    # error
    handShakeResponse = {
        'message': 'resource not accessible'
    }

    # get the data sent along
    sentData = request.GET.dict()

    # credentials
    sentEmail, sentPassword = sentData['email'], sentData['password']

    # validate
    userStatus, hospitalOBject = validateHandShakeUser(sentEmail, sentPassword)

    if userStatus is True:
        # get free assets
        idleAssets = getAvailableAssets(hospitalOBject[0])

        # own assets
        excludeList = getListOfDeletableAssets(hospitalOBject[3])

        # get a list of pending and accepted requests
        pendingRequests = getListOfRequests(hospitalOBject[3], False)

        acceptedRequests = getListOfRequests(hospitalOBject[3], True)

        incomingRequests = getListOfIncomingRequests(hospitalOBject[3])

        lentAssets = getListOfLentRequests(hospitalOBject[3])

        # get the history objects
        historyData = getOperationHistory(hospitalOBject[3])

        # get details 
        handShakeResponse = {
            'hospital': hospitalOBject[1],
            'assets': idleAssets,
            'avoid': excludeList,
            'tag': hospitalOBject[2],
            'pending': pendingRequests,
            'accepted': acceptedRequests,
            'incoming': incomingRequests,
            'lent': lentAssets,
            'history': historyData
        }

    else:
        # ignore
        pass

    return JsonResponse(handShakeResponse)


def getAttachedHospitalIncharge(requestEmail):
    # get hospital details
    inchargeObject = HospitalOfficers.objects.filter(employeeEmail=requestEmail).first()

    return inchargeObject


def deriveHospitalFromIncharge(requestEmail):
    # get the incharge
    inchargeObject = getAttachedHospitalIncharge(requestEmail)
    
    return inchargeObject.employeeHospital


    

def writeAssetDetail(request):
    # get the details
    assetDetails = request.GET.dict()

    # email
    accessEmail = assetDetails['who']

    # category
    assetCategory = assetDetails['category']

    assetLicensePlate = assetDetails['plate']

    assetCapacity = assetDetails['capacity']


    # get the hospital
    hospitalIncharge = getAttachedHospitalIncharge(accessEmail)

    # print("hospital Name:", hospitalIncharge.employeeHospital.hospitalName)

    if hospitalIncharge:
        # get the hospital
        attachedHospital = hospitalIncharge.employeeHospital

        # register
        ambulanceObject = AmbulanceAsset(
            assetOwner=attachedHospital,
            assetCategory=assetCategory,
            assetLicensePlate=assetLicensePlate,
            assetSittingCapacity=assetCapacity,
            serviceStatus=False
        )

        # save the object
        ambulanceObject.save()

        # get the associated primary key
        associatedPrimaryKey = ambulanceObject.pk

        replyMessage =  [associatedPrimaryKey, attachedHospital.hospitalUniqueId]

    else:
        replyMessage = 'seek authentication'

    # register the asset
    return JsonResponse({
        'message': replyMessage
    })


def wipeAssetFromDatabase(request):
    # get the data
    assetId = request.GET.get("asset-id")

    # get the asset itself
    ambulanceObject = AmbulanceAsset.objects.get(pk=assetId)

    # delete any associated requests for the asset
    ambulanceObject.assetOwner.incoming_requests.filter(assetId=assetId).delete()

    # print("Deleted the asset!")

    # finally delete the asset itself
    ambulanceObject.delete()

    return JsonResponse({
        'message': 'wiped'
    })


def recordAssetRequest(request):
    # get the asset ig
    assetId = request.GET.get('requested-id')

    # get the asset
    requestedAsset = AmbulanceAsset.objects.get(pk=assetId)

    # get the incharge email 
    inchargeEmail = request.GET.get('personnel-email')

    # owner
    ownerHospital = requestedAsset.assetOwner

    # requestor
    requestingHospital = deriveHospitalFromIncharge(inchargeEmail)

    # alert that the asset is booked now
    # requestedAsset.serviceStatus = True

    # recordAssetRequest.save()


    # create the request
    assetRequest = AssetRequest(
        assetId=assetId,
        assetOwner=ownerHospital,
        assetRequestor=requestingHospital,
        requestStatus=False
    )

    # save the request
    assetRequest.save()

    # get the request id
    # requestId = assetRequest.pk

    return JsonResponse({
        'message': 'sent'
    })




