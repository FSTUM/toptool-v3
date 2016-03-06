from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from .forms import AddForm, EditForm, AddStdForm, EditStdForm
from toptool_common.shortcuts import render


# list of tops for a meeting (allowed only by users with permission for the
# meetingtype or allowed for public if public-bit set)
# this is only used to embed the tops in the homepage
def list(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public: # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            return render(request, 'toptool_common/access_denied.html', {})

    tops = meeting.top_set.order_by('topid')

    context = {'meeting': meeting,
               'tops': tops}
    return render(request, 'tops/view.html', context)


# delete given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def delete(request, meeting_pk, topid):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        return render(request, 'toptool_common/access_denied.html', {})

    top = get_object_or_404(meeting.top_set, topid=topid)
    
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meeting.top_set.filter(topid=topid).delete()

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/del.html', context)


# add new top (allowed only by users with permission for the meetingtype or
# allowed for public if public-bit set)
def add(request, meeting_pk):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not meeting.meetingtype.public: # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meeting.meetingtype.permission()):
            return render(request, 'toptool_common/access_denied.html', {})
    if meeting.topdeadline_over and not request.user == \
            meeting.sitzungsleitung and not request.user.has_perm(
            meeting.meetingtype.admin_permission()):
        context = {'meeting': meeting,
                   'form': None}
        return render(request, 'tops/add.html', context)

    initial = {}
    if request.user.is_authenticated():
        initial['author'] = request.user.first_name + " " + request.user.last_name
        initial['email'] = request.user.email

    form = AddForm(request.POST or None, meeting=meeting, initial=initial)
    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'form': form}
    return render(request, 'tops/add.html', context)


# edit given top (allowed only by meetingtype-admin and sitzungsleitung)
@login_required
def edit(request, meeting_pk, topid):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    if not request.user.has_perm(meeting.meetingtype.admin_permission()) and not \
            request.user == meeting.sitzungsleitung:
        return render(request, 'toptool_common/access_denied.html', {})

    top = get_object_or_404(meeting.top_set, topid=topid)

    initial = {
        'title': top.title,
        'author': top.author,
        'email': top.email,
        'description': top.description,
        'protokoll_templ': top.protokoll_templ,
    }

    form = EditForm(request.POST or None, initial=initial)
    if form.is_valid():
        meeting.top_set.filter(topid=topid).update(
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author'],
            email=form.cleaned_data['email'],
            description=form.cleaned_data['description'],
            protokoll_templ=form.cleaned_data['protokoll_templ'],
        )

        return HttpResponseRedirect(reverse('viewmeeting', args=[meeting.id]))

    context = {'meeting': meeting,
               'top': top,
               'form': form}
    return render(request, 'tops/edit.html', context)


# delete standard top (allowed only by meetingtype-admin and staff)
@login_required
def delete_std(request, mt_pk, topid):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        return render(request, 'toptool_common/access_denied.html', {})

    standardtop = get_object_or_404(meetingtype.standardtop_set, topid=topid)
    
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.standardtop_set.filter(topid=topid).delete()

        return HttpResponseRedirect(reverse('liststdtops', args=[meetingtype.id]))

    context = {'meetingtype': meetingtype,
               'standardtop': standardtop,
               'form': form}
    return render(request, 'tops/del_std.html', context)


# add new standard top (allowed only by meetingtype-admin and staff)
@login_required
def add_std(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        return render(request, 'toptool_common/access_denied.html', {})

    form = AddStdForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('liststdtops', args=[meetingtype.id]))

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'tops/add_std.html', context)


# edit standard top (allowed only by meetingtype-admin and staff)
@login_required
def edit_std(request, mt_pk, topid):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        return render(request, 'toptool_common/access_denied.html', {})

    standardtop = get_object_or_404(meetingtype.standardtop_set, topid=topid)

    initial = {
        'title': standardtop.title,
        'description': standardtop.description,
        'protokoll_templ': standardtop.protokoll_templ,
        'topid': standardtop.topid,
    }

    form = EditStdForm(request.POST or None, initial=initial)
    if form.is_valid():
        meetingtype.standardtop_set.filter(pk=standardtop.pk).update(
            title=form.cleaned_data['title'],
            description=form.cleaned_data['description'],
            protokoll_templ=form.cleaned_data['protokoll_templ'],
            topid=form.cleaned_data['topid'],
        )

        return HttpResponseRedirect(reverse('liststdtops', args=[meetingtype.id]))

    context = {'meetingtype': meetingtype,
               'standardtop': standardtop,
               'form': form}
    return render(request, 'tops/edit_std.html', context)


