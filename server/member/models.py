from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class MemberImage(models.Model):
    member = models.ForeignKey(Member, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='member_image/')

    def __str__(self):
        return f"Image for {self.member.name}"