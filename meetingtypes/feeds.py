import datetime

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from django_ical.views import ICalFeed

from meetings.models import Meeting
from .models import MeetingType

class MeetingFeed(ICalFeed):
    def get_object(self, request, mt_pk):
        obj = get_object_or_404(MeetingType, pk=mt_pk)
        if not obj.public:
            raise PermissionDenied
        return obj

    def product_id(self, obj):
        return '-//fs.tum.de//meetings//{0}'.format(obj.id)

    def file_name(self, obj):
        return '{0}.ics'.format(obj.id)

    def items(self, obj):
        return obj.meeting_set.all().order_by('-time')

    def item_title(self, item):
        return item.get_title()

    def item_description(self, item):
        return ""

    def item_link(self, item):
        return reverse('viewmeeting', args=[item.meetingtype.id, item.id])

    def item_start_datetime(self, item):
        return item.time

    def item_end_datetime(self, item):
        return item.time + datetime.timedelta(hours=2)

    def item_location(self, item):
        return item.room