"""
Models for the profile app
"""
from users_accounts.models import UserAccount
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class SocialLinks(models.Model):
    """
    Model for social links.
    """

    site_name = models.CharField(max_length=255)
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # pylint: disable=R0903
    class Meta:
        """
        Meta class
        """

        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    # pylint: disable=E0307
    def __str__(self):
        return self.site_name


class UserProfile(models.Model):
    """
    Model for users profile.
    """

    user = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, related_name="user_profile"
    )
    firstname = models.CharField(max_length=65)
    lastname = models.CharField(max_length=65)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    average_rating = models.FloatField(default=0)

    def update_average_rating(self):
        ratings = Rating.objects.filter(rated_user=self.user)
        count = ratings.count()

        if count == 0:
            self.average_rating = 0
        else:
            total_rating = sum([rating.rating for rating in ratings])
            self.average_rating = total_rating / count

        self.save()

    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    social_media_accounts = models.ManyToManyField(
        SocialLinks, related_name="social_profiles"
    )


class Rating(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    rated_user = models.ForeignKey(
        UserAccount, related_name="rated_user", on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.rated_user.username}"
