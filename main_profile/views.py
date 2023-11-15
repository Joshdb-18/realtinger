"""
Views for profile app
"""
import uuid
import secrets

from accounts.models import UserAccount
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOwnerOrReadOnly
from .serializers import UserProfileserializer, SocialLinksSerializer, RatingSerializer


class CreateProfile(APIView):
    """
    Class to create a profile
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # pylint: disable=C0103
    # pylint: disable=W0613
    def get(self, request, pk):
        """
        Gets a user profile and display it
        """
        try:
            user = UserAccount.objects.get(pk=pk)
            user_profile = user.user_profile
            serializer = UserProfileserializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # pylint: disable=E1101
        except User.user_profile.RelatedObjectDoesNotExist:
            return Response(
                {"success": False, "message": "User does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # pylint: disable=C0103
    def post(self, request, pk):
        """
        Creates a profile
        """
        data = request.data
        user = get_object_or_404(UserAccount, pk=pk)

        if request.user != user:
            return Response(
                {"message": "User is not authorized", "success": False},
                status=status.HTTP_403_FORBIDDEN,
            )

        if hasattr(user, "user_profile"):
            error_response = {"message": "Profile already exists", "success": False}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        data["user"] = user.pk
        serializer = UserProfileserializer(data=data)
        image_file = request.FILES.get("profile_image")
        if image_file:
            unique_filename = (
                f"profile_{uuid.uuid4().hex}_{secrets.token_urlsafe(8)}_"
                f"{data['profile_image'].name}"
            )
            data["profile_image"].name = unique_filename

        if serializer.is_valid():
            # pylint: disable=W0612
            user_profile = serializer.save(user=user)
            response_data = {
                "message": "Profile successfully created",
                "success": True,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        error_response = {
            "message": "Invalid Request",
            "success": False,
            "errors": serializer.errors,
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    # pylint: disable=C0103
    def put(self, request, pk):
        """
        Updates a profile
        """
        data = request.data
        user = get_object_or_404(UserAccount, pk=pk)

        try:
            self.check_object_permissions(request, user.user_profile)

            user_profile = user.user_profile
            serializer = UserProfileserializer(user_profile, data=data, partial=True)
            image_file = request.FILES.get("profile_image")
            if image_file:
                unique_filename = (
                    f"profile_{uuid.uuid4().hex}_{secrets.token_urlsafe(8)}_"
                    f"{data['profile_image'].name}"
                )
                data["profile_image"].name = unique_filename

            if serializer.is_valid():
                user_profile = serializer.save()

                response_data = {
                    "message": "Profile successfully updated",
                    "success": True,
                    "data": serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            error_response = {
                "message": "Invalid Request",
                "success": False,
                "errors": serializer.errors,
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        # pylint: disable=E1101
        except User.user_profile.RelatedObjectDoesNotExist:
            return Response(
                {
                    "message": "User doesn't have a profile to edit",
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # pylint: disable=C0103
    def delete(self, request, pk):
        """
        Deletes a profile
        """
        try:
            user = UserAccount.objects.get(pk=pk)
            user_profile = user.user_profile

            self.check_object_permissions(request, user_profile)
            user.user_profile.delete()
            return Response(
                {"message": "Profile deleted successfully", "success": True},
                status=status.HTTP_200_OK,
            )
        # pylint: disable=E1101
        except UserAccount.user_profile.RelatedObjectDoesNotExist:
            return Response(
                {"success": False, "message": "User does have a profile to delete"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CreateSocial(APIView):
    """
    Class that handles a user social account
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # pylint: disable=C0103
    # pylint: disable=W0613
    def get(self, request, pk):
        """
        Gets and display the social account
        """
        user = get_object_or_404(UserAccount, pk=pk)

        if not hasattr(user, "user_profile"):
            error_response = {"message": "User has no profile", "success": False}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserAccount.objects.get(pk=pk)
            user_social = user.user_profile.social_media_accounts.all()
            if user_social.exists():
                social_accounts = []
                for accounts in user_social:
                    social_accounts.append(
                        {
                            "site_name": accounts.site_name,
                            "link": accounts.link,
                            "id": accounts.id,
                        }
                    )
                return Response(social_accounts, status=status.HTTP_200_OK)
            return Response(
                {
                    "success": False,
                    "message": "User haven't added a social account",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # pylint: disable=E1101
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # pylint: disable=C0103
    def post(self, request, pk):
        """
        Creates a social account
        """
        data = request.data
        user = get_object_or_404(UserAccount, pk=pk)

        self.check_object_permissions(request, user.user_profile)

        if not hasattr(user, "user_profile"):
            error_response = {"message": "User has no profile", "success": False}
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        user_profile = request.user.user_profile

        serializer = SocialLinksSerializer(data=data)
        if serializer.is_valid():
            social_link = serializer.save()
            user_profile.social_media_accounts.add(social_link)
            user_profile.save()
            response_data = {
                "message": "Social links created",
                "success": True,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        error_response = {
            "message": "Invalid Request",
            "success": False,
            "errors": serializer.errors,
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    # pylint: disable=C0103
    def put(self, request, pk):
        """
        Updates a social account
        """
        data = request.data
        user = get_object_or_404(UserAccount, pk=pk)

        try:

            self.check_object_permissions(request, user.user_profile)

            if not hasattr(user, "user_profile"):
                error_response = {"message": "User has no profile", "success": False}
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            user_profile = request.user.user_profile

            social_link_id = data.get("social_link_id")
            social_link = user_profile.social_media_accounts.filter(
                id=social_link_id
            ).first()

            if social_link:
                serializer = SocialLinksSerializer(
                    instance=social_link, data=data, partial=True
                )
                if serializer.is_valid():
                    # pylint: disable=W0612
                    updated_social_link = serializer.save()

                    response_data = {
                        "message": "Social link updated",
                        "success": True,
                        "data": serializer.data,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                error_response = {
                    "message": "Invalid Request",
                    "success": False,
                    "errors": serializer.errors,
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            error_response = {
                "message": "Social link not found",
                "success": False,
            }
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)
        # pylint: disable=E1101
        except UserAccount.user_profile.RelatedObjectDoesNotExist:
            return Response(
                {
                    "message": "User doesn't have any social account",
                    "success": False,
                }
            )

    # pylint: disable=C0103
    def delete(self, request, pk):
        """
        Deletes a social account
        """
        data = request.data
        user = get_object_or_404(UserAccount, pk=pk)

        try:

            self.check_object_permissions(request, user.user_profile)

            # Check if the user has a profile
            if not hasattr(user, "user_profile"):
                error_response = {"message": "User has no profile", "success": False}
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            # Get user profile
            user_profile = user.user_profile

            social_link_id = data["social_link_id"]
            social_account = user_profile.social_media_accounts.get(pk=social_link_id)
            if social_account:
                social_account.delete()
                response_data = {
                    "message": "Social account deleted successfully",
                    "success": True,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            error_response = {
                "message": "Invalid Request",
                "success": False,
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        # pylint: disable=E1101
        except UserAccount.user_profile.RelatedObjectDoesNotExist:
            return Response(
                {
                    "message": "User does not have a social account",
                    "success": False,
                }
            )


class UserRatingView(APIView):
    """
    Handles the rating system
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer

    def post(self, request, user_id):
        """
        Allows a user to rate a broker
        """
        rated_user_id = user_id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure the user can't rate themselves
        if request.user.id == int(rated_user_id):
            return Response(
                {"error": "You cannot rate yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.user_type == "land_broker":
            return Response(
                {"error": "Only a buyer can review a broker"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the user has already rated the target user
        existing_rating = Rating.objects.filter(
            user=request.user, rated_user_id=rated_user_id
        ).first()
        if existing_rating:
            return Response(
                {"error": "You have already rated this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user, rated_user_id=rated_user_id)

        # Update the average rating in the user profile
        rated_user_profile = UserProfile.objects.get(user__id=rated_user_id)
        rated_user_profile.update_average_rating()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, user_id):
        """
        Gets all a users rating
        """
        ratings = Rating.objects.filter(rated_user_id=user_id)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
