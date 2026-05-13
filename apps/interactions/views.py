from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.services import create_notification
from apps.recipes.models import Recipe
from .models import Comment, Rating, RecipeShare, SavedRecipe
from .serializers import (
    CommentSerializer,
    RatingSerializer,
    RecipeShareSerializer,
    SavedRecipeSerializer,
)


# ─── Ratings ───────────────────────────────────────────────────────────────────

@extend_schema(
    methods=["POST"],
    request=RatingSerializer,
    responses={200: RatingSerializer, 201: RatingSerializer},
    description="Create or update your rating (1–5) for a recipe.",
)
@extend_schema(
    methods=["DELETE"],
    request=None,
    responses={204: None, 404: OpenApiResponse(description="No rating found.")},
    description="Remove your rating for a recipe.",
)
class RecipeRatingView(APIView):
    """
    POST /api/v1/interactions/recipes/<id>/rate/
        body: {"score": 1-5}
    Creates or updates the calling user's rating for the recipe.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id, is_published=True)
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating, created = Rating.objects.update_or_create(
            recipe=recipe,
            user=request.user,
            defaults={"score": serializer.validated_data["score"]},
        )

        if created and recipe.author != request.user:
            create_notification(
                recipient=recipe.author,
                actor=request.user,
                verb=f"rated your recipe '{recipe.name}' {rating.score}/5",
                notification_type="rating",
                target_id=recipe.pk,
            )

        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        deleted, _ = Rating.objects.filter(recipe=recipe, user=request.user).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "No rating found."}, status=status.HTTP_404_NOT_FOUND)


class RecipeRatingListView(generics.ListAPIView):
    """GET /api/v1/interactions/recipes/<id>/ratings/ — all ratings for a recipe."""

    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Rating.objects.none()
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_id"])
        return Rating.objects.filter(recipe=recipe).select_related("user")


# ─── Comments ──────────────────────────────────────────────────────────────────

class RecipeCommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/interactions/recipes/<id>/comments/ — top-level comments with replies.
    POST /api/v1/interactions/recipes/<id>/comments/ — post a comment or reply.
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Comment.objects.none()
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_id"])
        return (
            Comment.objects.filter(recipe=recipe, parent=None)
            .select_related("author")
            .prefetch_related("replies__author")
        )

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs["recipe_id"])
        comment = serializer.save(author=self.request.user, recipe=recipe)
        # Notify recipe author (not self-comments)
        if recipe.author != self.request.user:
            create_notification(
                recipient=recipe.author,
                actor=self.request.user,
                verb=f"commented on your recipe '{recipe.name}'",
                notification_type="comment",
                target_id=recipe.pk,
            )
        return comment


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PATCH / DELETE /api/v1/interactions/comments/<id>/"""

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.select_related("author")

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method not in permissions.SAFE_METHODS and obj.author != request.user:
            self.permission_denied(request, message="You can only edit your own comments.")

    def perform_update(self, serializer):
        serializer.save(is_edited=True)


# ─── Saved Recipes (Favourites) ────────────────────────────────────────────────

class SavedRecipeListView(generics.ListAPIView):
    """GET /api/v1/interactions/saved/ — current user's saved recipes."""

    serializer_class = SavedRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SavedRecipe.objects.none()
        return (
            SavedRecipe.objects.filter(user=self.request.user)
            .select_related("recipe__author")
            .prefetch_related("recipe__tags", "recipe__meal_types")
        )


@extend_schema(
    request=None,
    responses={
        200: inline_serializer("UnsaveResponse", fields={"detail": serializers.CharField(), "saved": serializers.BooleanField()}),
        201: inline_serializer("SaveResponse", fields={"detail": serializers.CharField(), "saved": serializers.BooleanField()}),
    },
    description="Toggle save/unsave a recipe for the authenticated user.",
)
class RecipeSaveToggleView(APIView):
    """
    POST /api/v1/interactions/recipes/<id>/save/
    Saves or unsaves the recipe for the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id, is_published=True)
        saved, created = SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            saved.delete()
            return Response({"detail": "Recipe removed from saved.", "saved": False})
        return Response(
            {"detail": "Recipe saved.", "saved": True},
            status=status.HTTP_201_CREATED,
        )


# ─── Shares ────────────────────────────────────────────────────────────────────

@extend_schema(
    request=RecipeShareSerializer,
    responses={201: inline_serializer("ShareResponse", fields={
        "id": serializers.IntegerField(),
        "platform": serializers.CharField(),
        "created_at": serializers.DateTimeField(),
        "share_url": serializers.URLField(),
    })},
    description="Log a share event and receive a shareable URL.",
)
class RecipeShareView(APIView):
    """
    POST /api/v1/interactions/recipes/<id>/share/
        body: {"platform": "whatsapp"}
    Logs a share event and returns a shareable URL.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id, is_published=True)
        serializer = RecipeShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        share = serializer.save(
            recipe=recipe,
            shared_by=request.user if request.user.is_authenticated else None,
        )
        share_url = request.build_absolute_uri(f"/api/v1/recipes/{recipe.pk}/")
        return Response(
            {**RecipeShareSerializer(share).data, "share_url": share_url},
            status=status.HTTP_201_CREATED,
        )