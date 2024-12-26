from django.db import models

from catalogo_web_luque.settings import LIST_MAYO, LIST_MIN


class ModelArtic(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=150)
    priceMa = models.FloatField()
    priceMi = models.FloatField()
    active = models.BooleanField(default=True)
    imgs_path = models.FilePathField(path=None, null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.code},{self.description},may: {self.priceMa}, min: {self.priceMi}"

    # indexo el campo code
    # aumenta el rendimiento en la db
    class Meta:
        indexes = [
            models.Index(fields=['code'])
        ]


class ModelImgArtic(models.Model):
    path = models.FilePathField()
    artic = models.ForeignKey(
        ModelArtic, 
        on_delete=models.CASCADE,  # Define qué sucede al eliminar un artículo
        related_name="images",  # Nombre para acceder a las imágenes desde ModelArtic
        verbose_name="Article"
    )

    def __str__(self) -> str:
        return 

class ModelArticOnePrice(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=150)
    price = models.FloatField()
    
    def __str__(self) -> str:
        return f"{self.code},{self.description},{self.row},{self.col},may: {self.price}"

    # indexo el campo code
    # aumenta el rendimiento en la db
    class Meta:
        indexes = [
            models.Index(fields=['code'])
        ]
    def create_from_artic(self, artic, list_num):
        self.code = artic.code
        self.description = artic.description
        if list_num == LIST_MAYO:
            self.price = artic.priceMa
        elif list_num == LIST_MIN:
            self.price = artic.priceMi
            print(f"price mi: {self.price}")

        return self