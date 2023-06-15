from django.urls import path

from . import views

import socket

socket.socket(socket.AF_INET)

urlpatterns = [
    path("", views.loginView, name='loginpage'),
    path("home/", views.homeView, name='homepage'),
    path("users/", views.userManagementView, name='userpage'),
    path("requests/", views.requestsView, name='requestpage'),
    path("history/", views.fleetHistoryView, name='historypage'),
    path("logout/", views.logoutUserView, name='logoutuser'),
    path("register-hospital/", views.registerHospital, name='hosp-register'),
    path("delete-hospital/<int:hospitalId>/", views.deleteHospitalView, name='wipe-hospital'),
    path("register-incharge/", views.registerSystemAccessors, name='register-incharge'),
    path("delete-incharge/<int:userId>/", views.deleteInterfaceUser, name='delete-user'),
    path("handshake/", views.manageHandShake, name='manage-handshake'),
    path("write-asset/", views.writeAssetDetail, name='register-asset'),
]