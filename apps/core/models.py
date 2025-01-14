from django.db import models

from catalogo_web_luque.settings import LIST_MAYO, LIST_MIN


class ModelTag(models.Model):
    name = models.CharField(max_length=200, unique=True)  # El nombre de la etiqueta

    def __str__(self):
        return self.name

class ModelArtic(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=150)
    priceMa = models.FloatField()
    priceMi = models.FloatField()
    active = models.BooleanField(default=True)
    imgs_path = models.FilePathField(path=None, null=True, blank=True)
    tags =  models.ManyToManyField(ModelTag, related_name="articles", blank=True)
    
    def __str__(self) -> str:
        return f"{self.code},{self.description},may: {self.priceMa}, min: {self.priceMi}, tags: {self.tags}, active: {self.active}, imgs: {self.imgs_path}"

    def add_tag(self, txt_tag: str):
        tag = ModelTag.objects.filter(name=txt_tag).first()
        if not tag:
            tag = ModelTag(name=txt_tag)
            tag.save()

        if not self.tags.filter(id=tag.id).exists():
            self.tags.add(tag)
            self.save()

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
    tags = models.JSONField(default=list, blank=True)
    
    def __str__(self) -> str:
        return f"{self.code},{self.description},may: {self.price}"

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
            self.price = round(artic.priceMa, 2)
        elif list_num == LIST_MIN:
            self.price = round(artic.priceMi, 2)
            print(f"price mi: {self.price}")

        #self.save() 
        self.tags = artic.tags.all()
        #self.delete() 

        return self

    def formatted_price(self):
        return f"{self.price:.2f}" 