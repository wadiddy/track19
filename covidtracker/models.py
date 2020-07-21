from django.db import models

class Greeting(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)

class Location(models.Model):
    token = models.TextField(primary_key=True)
