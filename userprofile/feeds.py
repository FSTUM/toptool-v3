from datetime import datetime, timedelta
from uuid import UUID

from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_ical.views import ICalFeed

from meetings.models import Meeting
from meetingtypes.models import MeetingType

from .models import Profile


# pylint: disable=no-self-use
# pylint: disable=arguments-differ
class PersonalMeetingFeed(ICalFeed):
    file_name = "meetings.ics"

    def get_object(self, request: WSGIRequest, ical_key: UUID) -> User:
        profile = get_object_or_404(Profile, ical_key=ical_key)
        return profile.user

    def product_id(self, user: User) -> str:
        return f"-//fs.tum.de//meetings//user//{user.username}"

    def items(self, user: User) -> QuerySet[Meeting]:
        meetingtypes = MeetingType.objects.all().order_by("name")
        mts_with_perm = []
        for meetingtype in meetingtypes:
            if meetingtype.ical_key and user.has_perm(meetingtype.permission()):
                mts_with_perm.append(meetingtype.pk)
        reference_time = timezone.now() - timedelta(days=7 * 6)
        return Meeting.objects.filter(
            meetingtype__in=mts_with_perm,
            time__gte=reference_time,
        ).order_by("-time")

    def item_title(self, item: Meeting) -> str:
        title = item.get_title()
        if title != item.meetingtype.name:
            return f"{item.get_title()} ({item.meetingtype.name})"
        return title

    def item_description(self, item: Meeting) -> str:
        return ""

    def item_link(self, item: Meeting) -> str:
        return reverse("viewmeeting", args=[item.meetingtype.id, item.id])

    def item_start_datetime(self, item: Meeting) -> datetime:
        return item.time

    def item_end_datetime(self, item: Meeting) -> datetime:
        return item.time + timedelta(hours=2)

    def item_location(self, item: Meeting) -> str:
        return item.room