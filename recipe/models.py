import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


# Create your models here.


class Cuisine(models.Model):
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=20)


class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "Easy", "Easy"
        MEDIUM = "Medium", "Medium"
        HARD = "Hard", "Hard"

    class MealType(models.TextChoices):
        BREAKFAST = "Breakfast", "Breakfast"
        BRUNCH = "Brunch", "Brunch"
        LUNCH = "Lunch", "Lunch"
        DINNER = "Dinner", "Dinner"
        DESSERT = "Dessert", "Dessert"
        BEVERAGES = "Beverages", "Beverages"
        OTHER = "Other", "Other"

    class Category(models.TextChoices):
        VEGETARIAN = "Vegetarian", "Vegetarian"
        GLUTEN_FREE = "Gluten Free", "GlutenFree"
        LOW_CARB = "Low Carb", "LowCarb"
        PALEO = "Paleo", "Paleo"

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=255, db_index=True)
    prep_time_minutes = models.PositiveIntegerField(db_index=True)
    cook_time_minutes = models.PositiveIntegerField(db_index=True)
    desc = models.CharField(_('Short description'), max_length=200)
    servings = models.PositiveIntegerField()
    slug = models.SlugField(max_length=60, unique="id", blank=True)
    difficulty = models.CharField(
        max_length=10, choices=Difficulty, default=Difficulty.EASY
    )
    cuisine_type = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True)
    meal_type = models.CharField(
        max_length=10, choices=MealType, default=MealType.OTHER
    )
    calories_per_serving = models.PositiveIntegerField(db_index=True)
    chef = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    image = models.URLField()
    recipe_image = models.ImageField(
        default="default.jpg", upload_to="recipe_images/", blank=True, null=True
    )
    rating = models.FloatField(db_index=True)
    category = models.CharField(
        max_length=20, choices=Category, default=Category.VEGETARIAN
    )
    review_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Advanced tagging with django-taggit
    tags = TaggableManager()

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            # Composite index for common filtering combinations
            models.Index(fields=["difficulty", "cuisine"]),
            models.Index(fields=["prep_time_minutes", "cook_time_minutes"]),
            # Index for popular recipes
            models.Index(fields=["rating", "review_count"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    name = models.CharField(
        max_length=255, db_index=True
    )  # Indexed for ingredient searches

    def __str__(self):
        return self.name

    class Meta:
        # Ensure ingredient names are unique per recipe
        unique_together = ("recipe", "name")


class Instruction(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="instructions"
    )
    step_number = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"Step {self.step_number}"

    class Meta:
        ordering = ["step_number"]
        indexes = [
            # Optimize for step retrieval by recipe
            models.Index(fields=["recipe", "step_number"]),
        ]
        # Ensure step numbers are unique per recipe
        unique_together = ("recipe", "step_number")

