from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
# Create your models here.

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MealType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default="")
    image = models.URLField(blank=True, default="")
    image_file = models.ImageField(upload_to="recipes/", null=True, blank=True)

    ingredients = models.JSONField(default=list)
    instructions = models.JSONField(default=list)

    prep_time_minutes = models.PositiveSmallIntegerField(default=0)
    cook_time_minutes = models.PositiveSmallIntegerField(default=0)
    servings = models.PositiveSmallIntegerField(default=1)

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="Easy")
    cuisine = models.CharField(max_length=100, blank=True, default="", db_index=True)
    calories_per_serving = models.PositiveIntegerField(null=True, blank=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="recipes")
    meal_types = models.ManyToManyField(MealType, blank=True, related_name="recipes")

    # Denormalised rating aggregate (updated by signals)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    review_count = models.PositiveIntegerField(default=0)

    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["cuisine"]),
            models.Index(fields=["difficulty"]),
            models.Index(fields=["is_published", "-created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def total_time_minutes(self) -> int:
        return self.prep_time_minutes + self.cook_time_minutes