from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.http.response import JsonResponse
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from toptool.shortcuts import render
from meetingtypes.models import MeetingType
from .forms import ProfileForm

# edit user profile (allowed only by logged in users)
@login_required
def edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('editprofile')
    else:
        form = ProfileForm(instance=request.user.profile)

    meetingtypes = MeetingType.objects.order_by('name')
    mts_with_perm = []
    for meetingtype in meetingtypes:
        if request.user.has_perm(meetingtype.permission()):
            mts_with_perm.append(meetingtype)
    mt_preferences = {
        mtp.meetingtype.pk: mtp.sortid for mtp in
        request.user.meetingtypepreference_set.all()
    }
    if mt_preferences:
        max_sortid = max(mt_preferences.values()) + 1
    else:
        max_sortid = 1
    mts_with_perm.sort(
        key=lambda mt: (mt_preferences.get(mt.pk, max_sortid), mt.name)
    )

    ical_url = None
    if any(mt.ical_key for mt in mts_with_perm):
        ical_url = request.build_absolute_uri(
            reverse('personalical', args=[request.user.profile.ical_key])
        )

    context = {
        'form': form,
        'mts_with_perm': mts_with_perm,
        'ical_url': ical_url,
    }
    return render(request, 'userprofile/edit.html', context)


# sort meetingtypes (allowed only by logged in users)
@login_required
def sort_meetingtypes(request):
    if request.method == "POST":
        mts = [mt for mt in request.POST.getlist("mts[]", None) if mt]
        for i, mt in enumerate(mts):
            try:
                pk = mt.partition("_")[2]
            except IndexError:
                return HttpResponseBadRequest('')
            try:
                meetingtype = MeetingType.objects.get(pk=pk)
            except (MeetingType.DoesNotExist, ValidationError):
                return HttpResponseBadRequest('')
            request.user.meetingtypepreference_set.update_or_create(
                defaults={"sortid": i}, meetingtype=meetingtype)
        return JsonResponse({'success': True})
    return HttpResponseBadRequest('')
