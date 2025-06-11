from django.db import models
from user.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.name

class Post(models.Model):
    post_id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        ordering = ['-updated', '-created']

class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']