from django.urls import path
from .views import ViewSearchArtic, ViewSetCuil, SiaacFileUploadView, CreateClientView, NewClientRequest, ClientSuccess, DownloadArticsPDF

urlpatterns = [
    path('', ViewSearchArtic.as_view(), name='lists'),
    path('download/', DownloadArticsPDF.as_view(), name='download'),
    path('cuil/', ViewSetCuil.as_view(), name='get-cuil'),
    path('siaacfileupload/', SiaacFileUploadView.as_view(), name='siaacfileupload'),
    path('createclient/', CreateClientView.as_view(), name='createclient'),
    path('requestclient/', NewClientRequest.as_view(), name='requestclient'),
    path('clientsuccess/', ClientSuccess.as_view(), name='clientsuccess'),
]
