from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from meetingtypes.models import MeetingType


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                verbose_name=_("Benutzer"))
    color = models.CharField(
        _("Farbe"),
        max_length=30,
        blank=True,
    )


class MeetingTypePreference(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Benutzer"),
    )
    meetingtype = models.ForeignKey(
        MeetingType,
        on_delete=models.CASCADE,
        verbose_name=_("Sitzungsgruppe"),
    )
    sortid = models.IntegerField(
        _("Sort-ID"),
    )

    class Meta:
        unique_together = ("user", "meetingtype")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
