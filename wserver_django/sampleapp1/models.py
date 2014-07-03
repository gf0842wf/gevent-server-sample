from django.db import models

# Create your models here.

class Person(models.Model):

    def __unicode__(self):
        return self.name

    def is_vip_person(self):
        return self.name in ("fk", "gp")
    
    name = models.CharField(max_length=20)
    desc = models.CharField(max_length=50)

class Car(models.Model):
    
    def __unicode__(self):
        return self.name
    
    name = models.CharField(max_length=20)
    owner = models.ForeignKey(Person)
