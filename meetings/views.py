from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


from .models import Meeting

def view(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    tops = meeting.top_set.order_by('topid')
    attendees = meeting.attendees.order_by('name')

    context = {'meeting': meeting,
               'tops': tops,
               'attendees': attendees}
    return render(request, 'meetings/view.html', context)

def send_tops(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    meeting.send_mail(request)

    return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

def edit(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    # TODO

