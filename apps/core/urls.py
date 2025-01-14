

from django.urls import path
from .views import ViewSearchArtic, ViewSetCuil, vincule_imgs, SiaacFileUploadView, create_tags, get_tarugos_yeso

urlpatterns = [

    path('', ViewSearchArtic.as_view(), name='listas-xlsx'),
    path('cuil/', ViewSetCuil.as_view(), name='get-cuil'),
    path('tmpaddimg/', vincule_imgs, name='tmp-imgs'),
    path('siaacfileupload/', SiaacFileUploadView.as_view(), name='siaacfileupload'),
    path('tmptags/', create_tags, name='tmp-tags'),
    path('gettarugos/', get_tarugos_yeso, name='get-taye'),

   
]
