from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Rating


def _refresh_recipe_rating(recipe):
    """Recompute the denormalised rating fields on the recipe."""
    agg = Rating.objects.filter(recipe=recipe).aggregate(avg=Avg("score"))
    avg = round(agg["avg"] or 0, 1)
    count = Rating.objects.filter(recipe=recipe).count()
    recipe.__class__.objects.filter(pk=recipe.pk).update(rating=avg, review_count=count)


@receiver(post_save, sender=Rating)
def on_rating_save(sender, instance, **kwargs):
    _refresh_recipe_rating(instance.recipe)


@receiver(post_delete, sender=Rating)
def on_rating_delete(sender, instance, **kwargs):
    _refresh_recipe_rating(instance.recipe)
    