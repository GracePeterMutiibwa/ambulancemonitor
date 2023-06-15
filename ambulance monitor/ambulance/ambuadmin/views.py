from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Hospital, HospitalOfficers, AmbulanceAsset
from django.http import JsonResponse




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

            print("User Logged in:", userObject.username)

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
def requestsView(request):
    return render(request, "ambuadmin/request-control.html")

@login_required(login_url="loginpage")
def fleetHistoryView(request):
    return render(request, "ambuadmin/fleet-history.html")


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
        hospitalObject = Hospital(hospitalName=submittedName)

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
        return True, userObject.employeeHospital.id
    
    else:
        return False, None


def getAvailableAssets(idToIgnore):
    # get
    assets = AmbulanceAsset.objects.all()

    # names of assets to ignore
    assetNamesToFlag = []

    # idle
    idleAssets = []

    # filter
    for eachAsset in assets:
        if (eachAsset.assetOwner.id != idToIgnore and eachAsset.serviceStatus is False):
            # store the details
            idleAssets.append({
                eachAsset.assetLicensePlate: (
                                                eachAsset.assetOwner.hospitalName,
                                                eachAsset.assetCategory,
                                                eachAsset.assetSittingCapacity
                                            )
            })

        else:
            # record the license plate
            assetNamesToFlag.append(
                    (
                        eachAsset.assetLicensePlate,
                        eachAsset.id
                    )
                )
            

    
    return idleAssets, assetNamesToFlag


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
    userStatus, hospitalId = validateHandShakeUser(sentEmail, sentPassword)

    if userStatus is True:
        # get free assets
        idleAssets, excludeList = getAvailableAssets(hospitalId)

        # get details 
        handShakeResponse = {
            'assets': idleAssets,
            'avoid': excludeList
        }

    else:
        # ignore
        pass

    return JsonResponse(handShakeResponse)


def getAttachedHospital(requestEmail):
    # get hospital details
    hospitalObject = HospitalOfficers.objects.filter(employeeEmail=requestEmail).first()

    return hospitalObject
    

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
    hospitalIncharge = getAttachedHospital(accessEmail)

    print("hospital Name:", hospitalIncharge.employeeHospital.hospitalName)

    if hospitalIncharge:
        # register
        ambulanceObject = AmbulanceAsset(
            assetOwner=hospitalIncharge.employeeHospital,
            assetCategory=assetCategory,
            assetLicensePlate=assetLicensePlate,
            assetSittingCapacity=assetCapacity,
            serviceStatus=False
        )

        # save the object
        ambulanceObject.save()

        replyMessage =  'asset registered'

    else:
        replyMessage = 'seek authentication'

    # register the asset
    return JsonResponse({
        'message': replyMessage
    })


