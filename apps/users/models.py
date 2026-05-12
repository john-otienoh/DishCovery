from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, default="")
    avatar = models.ImageField(upload_to='avatars/',  blank=True, null=True)
    website = models.URLField(blank=True, default="")
    dietary_preferences = models.JSONField(
        default=list,
        blank=True,
        help_text="e.g. ['vegan', 'gluten-free']",
    )
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    recipe_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
    
    def __str__(self) -> str:
        return self.email
    

class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following_set",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers_set",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]
        indexes =[
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.follower.username} -> {self.following.username}"