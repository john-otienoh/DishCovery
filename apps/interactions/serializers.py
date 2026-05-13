# Create your views here.
from rest_framework import serializers

from apps.recipes.serializers import RecipeListSerializer
from apps.users.serializers import UserPublicSerializer
from .models import Comment, Rating, RecipeShare, SavedRecipe


class RatingSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ("id", "user", "score", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate_score(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Score must be between 1 and 5.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "author", "parent", "body", "is_edited", "replies", "created_at", "updated_at")
        read_only_fields = ("id", "author", "is_edited", "created_at", "updated_at")

    def get_replies(self, obj):
        """Return one level of replies (children only)."""
        if obj.parent is not None:
            return []
        qs = obj.replies.select_related("author").order_by("created_at")
        return CommentSerializer(qs, many=True).data


class SavedRecipeSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer(read_only=True)

    class Meta:
        model = SavedRecipe
        fields = ("id", "recipe", "created_at")
        read_only_fields = ("id", "created_at")


class RecipeShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeShare
        fields = ("id", "platform", "created_at")
        read_only_fields = ("id", "created_at")