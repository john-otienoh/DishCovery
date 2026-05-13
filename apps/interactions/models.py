from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.recipes.models import Recipe

# Create your models here.
User = get_user_model()


class Rating(models.Model):

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("recipe", "user")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipe"])]

    def __str__(self) -> str:
        return f"{self.user.username} rated {self.recipe.name}: {self.score}/5"


class Comment(models.Model):
    """A user comment on a recipe, supports nested replies."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    body = models.TextField()
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipe"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        return f"{self.author.username} on {self.recipe.name}"


class SavedRecipe(models.Model):
    """A recipe saved to a user's personal collection."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_recipes")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="saves")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user"])]

    def __str__(self) -> str:
        return f"{self.user.username} saved {self.recipe.name}"


class RecipeShare(models.Model):
    """Tracks sharing events for analytics."""

    PLATFORM_CHOICES = [
        ("email", "Email"),
        ("twitter", "Twitter/X"),
        ("facebook", "Facebook"),
        ("whatsapp", "WhatsApp"),
        ("link", "Copy Link"),
        ("other", "Other"),
    ]

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="shares")
    shared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shares",
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="link")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["recipe"])]

    def __str__(self) -> str:
        return f"{self.recipe.name} shared via {self.platform}"