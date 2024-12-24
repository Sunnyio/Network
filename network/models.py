from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    followers = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        related_name='following',
        blank=True
    )

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    class Meta:
        ordering = ['-date']  # Show newest posts first

    def __str__(self):
        return f"{self.user} posted: {self.content[:50]}..."

    @property
    def like_count(self):
        return self.likes.count()
