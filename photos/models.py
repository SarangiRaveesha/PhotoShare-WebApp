from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('private', 'Private'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    caption = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.id}"

#in Photo & PhotoTag
class PhotoTag(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='tags')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='photo_tags')
    username_snapshot = models.CharField(max_length=150)

    class Meta:
        unique_together = ('photo', 'username_snapshot')

    def __str__(self):
        return f"{self.username_snapshot} tagged in photo {self.photo.id}"
#PhotoTag
    @property
    def display_name(self):
        return self.user.username if self.user else self.username_snapshot


class Comment(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def display_name(self):
        return self.author.username if self.author else "Deleted User"


class Like(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('photo', 'user')


class Reaction(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)

    class Meta:
        unique_together = ('comment', 'user', 'emoji')
