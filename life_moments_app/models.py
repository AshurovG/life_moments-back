from django.db import models

# Create your models here.
class Books(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'books'