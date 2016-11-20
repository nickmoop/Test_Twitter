from django.db import models


class TwitterUser(models.Model):
    token = models.CharField(max_length=100)
    username = models.CharField(max_length=80)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)
