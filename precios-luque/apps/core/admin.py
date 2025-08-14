from django.contrib import admin
from .models import ModelArtic, ModelTag, ModelClient, ModelImgArtic

admin.site.register(ModelArtic)
admin.site.register(ModelTag)
admin.site.register(ModelClient)
admin.site.register(ModelImgArtic)
