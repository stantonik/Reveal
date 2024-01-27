from django.db import models

# Create your models here.

class Author(models.Model):
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
  description = models.CharField(max_length=255)
  imgsrc = models.CharField(max_length=255)
