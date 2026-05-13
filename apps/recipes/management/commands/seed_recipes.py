"""
Usage:
    python manage.py seed_recipes
    python manage.py seed_recipes --file 
    python manage.py seed_recipes --clear   
"""

import json
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.recipes.models import MealType, Recipe, Tag

User = get_user_model()

DEFAULT_JSON = Path(__file__).resolve().parents[5] / "DishCovery" / "scripts/recipes.json"


class Command(BaseCommand):
    help = "Seed the database with recipes from recipes.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=str(DEFAULT_JSON),
            help="Path to the recipes JSON file",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing recipes before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        filepath = options["file"]
        if not os.path.exists(filepath):
            self.stderr.write(self.style.ERROR(f"File not found: {filepath}"))
            return

        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        recipes_data = data.get("recipes", data) if isinstance(data, dict) else data

        if options["clear"]:
            self.stdout.write("Clearing existing recipes…")
            Recipe.objects.all().delete()
            Tag.objects.all().delete()
            MealType.objects.all().delete()

        # Ensure a seed superuser exists
        seed_user, created = User.objects.get_or_create(
            username="seed_admin",
            defaults={
                "email": "seed@dishcovery.local",
                "is_staff": True,
            },
        )
        if created:
            seed_user.set_password("seed_admin_pass")
            seed_user.save()
            self.stdout.write(self.style.SUCCESS("Created seed_admin user"))

        created_count = 0
        skipped_count = 0

        for item in recipes_data:
            name = item.get("name", "").strip()
            if not name:
                continue

            if Recipe.objects.filter(name=name).exists():
                skipped_count += 1
                continue

            # Resolve tags
            tag_objs = []
            for tag_name in item.get("tags", []):
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                tag, _ = Tag.objects.get_or_create(
                    slug=slugify(tag_name),
                    defaults={"name": tag_name},
                )
                tag_objs.append(tag)

            # Resolve meal types
            meal_type_objs = []
            for mt_name in item.get("mealType", []):
                mt_name = mt_name.strip()
                if not mt_name:
                    continue
                mt, _ = MealType.objects.get_or_create(name=mt_name)
                meal_type_objs.append(mt)

            recipe = Recipe.objects.create(
                author=seed_user,
                name=name,
                image=item.get("image", ""),
                ingredients=item.get("ingredients", []),
                instructions=item.get("instructions", []),
                prep_time_minutes=item.get("prepTimeMinutes", 0),
                cook_time_minutes=item.get("cookTimeMinutes", 0),
                servings=item.get("servings", 1),
                difficulty=item.get("difficulty", "Easy"),
                cuisine=item.get("cuisine", ""),
                calories_per_serving=item.get("caloriesPerServing"),
                rating=item.get("rating", 0),
                review_count=item.get("reviewCount", 0),
                is_published=True,
            )
            recipe.tags.set(tag_objs)
            recipe.meal_types.set(meal_type_objs)
            created_count += 1

        # Refresh author recipe count
        User.objects.filter(pk=seed_user.pk).update(recipes_count=created_count)

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created_count} recipe(s) created, {skipped_count} skipped."
            )
        )