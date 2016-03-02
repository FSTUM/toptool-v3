from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django import forms
from django.conf import settings

from .models import MeetingType
from tops.models import Top
from protokolle.models import Protokoll
from meetings.models import Meeting
from .forms import MTForm, MTAddForm, MeetingAddForm

# list all meetingtypes the user is a member of
# (allowed only by logged users)
@login_required
def index(request):
    meetingtypes = MeetingType.objects.order_by('name')

    context = {'meetingtypes': meetingtypes}
    return render(request, 'meetingtypes/index.html', context)

# admin interface: view all meetingtypes (allowed only by staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def index_all(request):
    meetingtypes = MeetingType.objects.order_by('name')

    context = {'meetingtypes': meetingtypes}
    return render(request, 'meetingtypes/index_all.html', context)

# view single meetingtype (allowed only by users with permission for that
# meetingtype or allowed for public if public-bit set)
def view(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not meetingtype.public: # public access disabled
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        if not request.user.has_perm(meetingtype.permission()):
            raise Http404("Access Denied")

    meetings = meetingtype.meeting_set.order_by('time')

    context = {'meetingtype': meetingtype,
               'meetings': meetings}
    return render(request, 'meetingtypes/view.html', context)

# create meetingtype (allowed only by staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def add(request):
    form = MTAddForm(request.POST or None)
    if form.is_valid():
        content_type = ContentType.objects.get_for_model(MeetingType)
        
        name=form.cleaned_data['name']
        shortname=form.cleaned_data['shortname']
        groups=form.cleaned_data['groups']
        users=form.cleaned_data['users']
        admin_groups=form.cleaned_data['admin_groups']
        admin_users=form.cleaned_data['admin_users']

        permission = Permission.objects.create(codename=shortname,
            name="permission for " + name, content_type=content_type)

        admin_permission = Permission.objects.create(
            codename=shortname + MeetingType.ADMIN,
            name="admin_permission for " + name,
            content_type=content_type)

        for g in groups:
            g.permissions.add(permission)
        for u in users:
            u.user_permissions.add(permission)
        for g in admin_groups:
            g.permissions.add(permission)
            g.permissions.add(admin_permission)
        for u in admin_users:
            u.user_permissions.add(permission)
            u.user_permissions.add(admin_permission)

        MeetingType.objects.create(
            name=name,
            shortname=shortname,
            mailinglist=form.cleaned_data['mailinglist'],
            approve=form.cleaned_data['approve'],
            attendance=form.cleaned_data['attendance'],
            public=form.cleaned_data['public'],
        )

        return redirect('allmts')

    context = {'form': form}
    return render(request, 'meetingtypes/add.html', context)

# edit meetingtype (allowed only by meetingtype-admin or staff)
@login_required
def edit(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()) and not \
            request.user.is_staff:
        raise Http404("Access Denied")
    
    groups = Group.objects.filter(
        permissions=meetingtype.get_permission())
    users = User.objects.filter(
        user_permissions=meetingtype.get_permission())
    admin_groups = Group.objects.filter(
        permissions=meetingtype.get_admin_permission())
    admin_users = User.objects.filter(
        user_permissions=meetingtype.get_admin_permission())

    initial_values = {
        'name': meetingtype.name,
        'groups': groups,
        'users': users,
        'admin_groups': admin_groups,
        'admin_users': admin_users,
        'mailinglist': meetingtype.mailinglist,
        'approve': meetingtype.approve,
        'attendance': meetingtype.attendance,
        'public': meetingtype.public,
    }

    form = MTForm(request.POST or None, initial=initial_values)
    if form.is_valid():
        content_type = ContentType.objects.get_for_model(MeetingType)
        
        #groups = groups.iterator()
        #users = users.iterator()
        #admin_groups = groups.iterator()
        #admin_users = users.iterator()

        name=form.cleaned_data['name']
        shortname=meetingtype.shortname # the shortname cannot be changed
        groups_=form.cleaned_data['groups']
        users_=form.cleaned_data['users']
        admin_groups_=form.cleaned_data['admin_groups']
        admin_users_=form.cleaned_data['admin_users']

        permission = meetingtype.get_permission()
        admin_permission = meetingtype.get_admin_permission()

        # first remove all revoked permissions
        for g in groups:
            if g not in groups_:
                g.permissions.remove(permission)
        for u in users:
            if u not in users_:
                u.user_permissions.remove(permission)
        for g in admin_groups:
            if g not in admin_groups_:
                g.permissions.remove(permission)
                g.permissions.remove(admin_permission)
        for u in admin_users:
            if u not in admin_users_:
                u.user_permissions.remove(permission)
                u.user_permissions.remove(admin_permission)

        # then set all new permissions
        for g in groups_:
            if g not in groups:
                g.permissions.add(permission)
        for u in users_:
            if u not in users:
                u.user_permissions.add(permission)
        for g in admin_groups_:
            if g not in admin_groups:
                g.permissions.add(permission)
                g.permissions.add(admin_permission)
        for u in admin_users_:
            if u not in admin_users:
                u.user_permissions.add(permission)
                u.user_permissions.add(admin_permission)

        MeetingType.objects.filter(pk=mt_pk).update(
            name=name,
            shortname=shortname,
            mailinglist=form.cleaned_data['mailinglist'],
            approve=form.cleaned_data['approve'],
            attendance=form.cleaned_data['attendance'],
            public=form.cleaned_data['public'],
        )

        return redirect('viewmt', meetingtype.id)

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetingtypes/edit.html', context)


# delete meetingtype (allowed only by staff)
@login_required
@user_passes_test(lambda u: u.is_staff)
def delete(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    form = forms.Form(request.POST or None)
    if form.is_valid():
        meetingtype.get_permission().delete()
        meetingtype.get_admin_permission().delete()
        Top.objects.filter(meeting__meetingtype=meetingtype).delete()
        Protokoll.objects.filter(meeting__meetingtype=meetingtype).delete()
        Meeting.objects.filter(meetingtype=meetingtype).delete()
        meetingtype.delete()
        
        return redirect('allmts')

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetingtypes/del.html', context)


# create new meeting (allowed only by meetingtype-admin)
@login_required
def add_meeting(request, mt_pk):
    meetingtype = get_object_or_404(MeetingType, pk=mt_pk)
    if not request.user.has_perm(meetingtype.admin_permission()):
        raise Http404("Access Denied")

    form = MeetingAddForm(request.POST or None, meetingtype=meetingtype)
    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('viewmt', args=[meetingtype.id]))

    context = {'meetingtype': meetingtype,
               'form': form}
    return render(request, 'meetingtypes/add_meeting.html', context)


