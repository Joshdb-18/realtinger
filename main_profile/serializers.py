"""
Serializer for the user profile
"""
from rest_framework import serializers
from .models import UserProfile, SocialLinks, Rating


class SocialLinksSerializer(serializers.ModelSerializer):
    """
    Serializer for SocialLinks model.
    """

    # pylint: disable=R0903
    class Meta:
        """
        Meta class for SocialLinksSerializer.
        """

        model = SocialLinks
        fields = ["id", "site_name", "link"]

    def create(self, validated_data):
        """
        Create and return a new SocialLinks instance.
        """
        # pylint: disable=E1101
        social_media = SocialLinks.objects.create(**validated_data)
        return social_media


class RatingSerializer(serializers.ModelSerializer):
    """
    Serialiazer class for the ratings (JSON)
    """

    class Meta:
        """
        Meta class for RatingSerializer
        """

        model = Rating
        fields = "__all__"


class UserProfileserializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """

    social_media_accounts = SocialLinksSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta class for UserProfileSerializee.
        """

        model = UserProfile
        fields = "__all__"

    def validate(self, attrs):
        """
        Checks if the firstname and lastname starts with a capital letter
        """
        if "firstname" in attrs and attrs["firstname"][0].islower():
            attrs["firstname"] = attrs["firstname"].capitalize()

        if "lastname" in attrs and attrs["lastname"][0].islower():
            attrs["lastname"] = attrs["lastname"].capitalize()

        return attrs

    def create(self, validated_data):
        """
        Create and return a UserProfile instance.
        """
        # pylint: disable=E1101
        profile = UserProfile.objects.create(**validated_data)
        return profile
