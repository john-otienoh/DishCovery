from rest_framework import serializers

from apps.users.serializers import UserPublicSerializer
from .models import MealType, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = ("id", "slug")


class MealTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealType
        fields = ("id", "name")
        read_only_fields = ("id",)


class RecipeListSerializer(serializers.ModelSerializer):

    author = UserPublicSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    meal_types = MealTypeSerializer(many=True, read_only=True)
    total_time_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "description",
            "image",
            "author",
            "difficulty",
            "cuisine",
            "prep_time_minutes",
            "cook_time_minutes",
            "total_time_minutes",
            "servings",
            "calories_per_serving",
            "rating",
            "review_count",
            "tags",
            "meal_types",
            "is_published",
            "created_at",
        )
        read_only_fields = ("id", "rating", "review_count", "author", "created_at")


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Full recipe with ingredients and instructions."""

    author = UserPublicSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    meal_types = MealTypeSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        required=False,
        source="tags",
    )
    meal_type_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MealType.objects.all(),
        write_only=True,
        required=False,
        source="meal_types",
    )
    total_time_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "description",
            "image",
            "image_file",
            "author",
            "ingredients",
            "instructions",
            "prep_time_minutes",
            "cook_time_minutes",
            "total_time_minutes",
            "servings",
            "difficulty",
            "cuisine",
            "calories_per_serving",
            "tags",
            "tag_ids",
            "meal_types",
            "meal_type_ids",
            "rating",
            "review_count",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "rating", "review_count", "created_at", "updated_at")

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        meal_types = validated_data.pop("meal_types", [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.meal_types.set(meal_types)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        meal_types = validated_data.pop("meal_types", None)
        recipe = super().update(instance, validated_data)
        if tags is not None:
            recipe.tags.set(tags)
        if meal_types is not None:
            recipe.meal_types.set(meal_types)
        return recipe
    