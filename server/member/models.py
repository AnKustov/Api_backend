from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='member_image/', blank=True)

    def __str__(self):
        return self.name
    
