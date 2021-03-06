from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from meetingtypes.models import MeetingType
from toptool.utils.permission import auth_login_required
from toptool.utils.shortcuts import get_permitted_mts_sorted, render
from toptool.utils.typing import AuthWSGIRequest

from .forms import ProfileForm


@auth_login_required()
def edit_profile(request: AuthWSGIRequest) -> HttpResponse:
    """
    Edit user profile.

    @permission: allowed only by logged-in users
    @param request: a WSGIRequest by a logged-in user
    @return: a HttpResponse
    """

    form = ProfileForm(request.POST or None, instance=request.user.profile)
    if form.is_valid():
        form.save()
        return redirect("userprofile:edit_profile")

    mts_with_perm = get_permitted_mts_sorted(request.user)

    ical_url = None
    if any(mt.ical_key for mt in mts_with_perm):
        ical_url = request.build_absolute_uri(
            reverse("userprofile:personal_ical_meeting_feed", args=[request.user.profile.ical_key]),
        )

    context = {
        "form": form,
        "mts_with_perm": mts_with_perm,
        "ical_url": ical_url,
    }
    return render(request, "userprofile/edit.html", context)


@auth_login_required()
def sort_meetingtypes(request: AuthWSGIRequest) -> HttpResponse:
    """
    Enables the user to sort their meetingtypes.

    @permission: allowed only by logged-in users
    @param request: a WSGIRequest by a logged-in user
    @return: a HttpResponse
    """

    if request.method == "POST":
        meetingtypes = [mt for mt in request.POST.getlist("mts[]") if mt]
        for counter, meetingtype_id in enumerate(meetingtypes):
            try:
                meetingtype_pk = meetingtype_id.partition("_")[2]
            except IndexError:
                return HttpResponseBadRequest()
            try:
                meetingtype = MeetingType.objects.get(pk=meetingtype_pk)
            except (MeetingType.DoesNotExist, ValidationError):
                return HttpResponseBadRequest()
            request.user.meetingtypepreference_set.update_or_create(
                defaults={"sortid": counter},
                meetingtype=meetingtype,
            )
        return JsonResponse({"success": True})
    return HttpResponseBadRequest()
