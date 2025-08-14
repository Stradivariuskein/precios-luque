from django.db import models
import secrets

class ModelRequestClient(models.Model):
    LIST_NUMBER_CHOICES = [
        ("1", 'Minorista'),
        ("5", 'Mayorista'),
    ]
    BUSSINES_CHOISES = [
        ("Distribuidor","Distribuidor"),
        ("Mayorista","Mayorista"),
        ("Buloneria","Buloneria"),
        ("Ferreteria","Ferreteria"),
        ("Revendedor","Revendedor"),
    ]

    

    cuil = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=36)
    empress_name = models.CharField(max_length=50)
    tel = models.CharField(max_length=24)
    email = models.CharField(max_length=64)
    bussines = models.CharField(max_length=16, choices=BUSSINES_CHOISES)
    message = models.CharField(max_length=512)
    token = models.CharField(max_length=64, unique=True,)
    

    def _generate_token(self):
        self.token=secrets.token_urlsafe(48)  # genera ~64 caracteres seguros