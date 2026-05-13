import django_filters
from django.db.models import F

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Allows filtering recipes via query parameters:
        ?cuisine=Italian
        ?difficulty=Easy
        ?min_calories=100&max_calories=500
        ?max_time=30
        ?meal_type=Dinner
        ?tag=Pasta
    """

    cuisine = django_filters.CharFilter(lookup_expr="iexact")
    difficulty = django_filters.ChoiceFilter(choices=Recipe.DIFFICULTY_CHOICES)
    min_calories = django_filters.NumberFilter(field_name="calories_per_serving", lookup_expr="gte")
    max_calories = django_filters.NumberFilter(field_name="calories_per_serving", lookup_expr="lte")
    max_time = django_filters.NumberFilter(method="filter_max_total_time")
    meal_type = django_filters.CharFilter(field_name="meal_types__name", lookup_expr="iexact")
    tag = django_filters.CharFilter(field_name="tags__name", lookup_expr="iexact")
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr="gte")
    author = django_filters.CharFilter(field_name="author__username", lookup_expr="iexact")

    class Meta:
        model = Recipe
        fields = [
            "cuisine",
            "difficulty",
            "min_calories",
            "max_calories",
            "max_time",
            "meal_type",
            "tag",
            "min_rating",
            "author",
        ]

    def filter_max_total_time(self, queryset, name, value):
        """Filter where prep + cook <= max_time."""
        return queryset.annotate(
            total_time=F("prep_time_minutes") + F("cook_time_minutes")
        ).filter(total_time__lte=value)