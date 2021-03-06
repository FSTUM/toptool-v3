import os
import random
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import Client, RequestFactory
from mixer.backend.django import mixer

from meetings.models import Meeting
from meetingtypes.models import MeetingType
from persons.models import Attendee, Function, Person
from protokolle.models import Attachment, Protokoll
from tops.models import StandardTop, Top

pytestmark = pytest.mark.django_db
# pylint: disable=too-many-branches
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init
# pylint: disable=super-with-arguments
# pylint: disable=missing-function-docstring


def if_then_else(test, then_func, else_func):
    def if_then_else_checker(*args, **kwargs):
        if test(*args, **kwargs):
            then_func(*args, **kwargs)
        else:
            else_func(*args, **kwargs)

    return if_then_else_checker


def raises_error(error):
    def error_checker(_url, _redirect_url, view, *args):
        with pytest.raises(error):
            _ = view(*args)

    return error_checker


def redirect_to_login(url, _redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 302, "Should redirect to login"
    assert resp.url == "/login/?next=" + url, "Should redirect to login"


def redirect_to_url(_url, redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 302, "Should redirect to given url"
    if redirect_url is not None:
        assert resp.url == redirect_url, "Should redirect to given url"


def accessible(_url, _redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 200, "Should be accessible"


def permission_denied(_url, _redirect_url, view, *args):
    with pytest.raises((PermissionDenied, AssertionError)):
        resp = view(*args)
        assert resp.status_code != 403, "Should be a 403 - permission denied"


def not_found(_url, _redirect_url, view, *args):
    with pytest.raises((Http404, AssertionError)):
        resp = view(*args)
        assert resp.status_code != 404, "Should be a 404 - not found"


def bad_request(_url, _redirect_url, view, *args):
    resp = view(*args)
    assert resp.status_code == 400, "Should be a 400 - bad request"


class AbstractTestView:
    def setup_method(self):
        self.url = ""
        self.anonymous_public = None
        self.anonymous_not_public = None
        self.logged_in_public = None
        self.logged_in_with_rights = None
        self.logged_in_with_admin_rights = None
        self.logged_in_without_rights = None
        self.logged_in_sitzungsleitung = None
        self.logged_in_protokollant = None
        self.admin_public = None
        self.admin_not_public = None
        self.args = []
        self.redirect_url = None
        self.use_mt = True
        self.use_meeting = True
        self.use_meeting_for_redirect = False
        self.use_mt_for_redirect = False
        self.use_top = False
        self.use_std_top = False
        self.use_attachment = False
        self.use_attendee = False
        self.use_func = False
        self.use_person = False
        self.test_view = True
        self.filetype = random.choice(("html", "pdf", "txt"))
        self.prepared = False

    def teardown_method(self):
        try:
            fullname = self.protokoll.filepath + "." + self.filetype
            if os.path.getsize(fullname) == 0:
                os.remove(fullname)
        except AttributeError:
            pass

    @pytest.fixture(autouse=True)
    def prepare(self):
        self.prepare_variables()

    def prepare_variables(self):
        if self.prepared:
            return
        self.mt1 = mixer.blend(
            MeetingType,
            id="abc",
            public=False,
            tops=True,
            top_perms="public",
            protokoll=True,
            standard_tops=True,
            ical_key=uuid.uuid4,
            mailinglist="abc@de.fg",
        )
        self.mt2 = mixer.blend(
            MeetingType,
            id="abcd",
            public=False,
            tops=True,
            top_perms="public",
            protokoll=True,
            standard_tops=True,
            ical_key=uuid.uuid4,
            mailinglist="abc@de.fg",
        )
        self.meeting = mixer.blend(Meeting, meetingtype=self.mt1)
        self.top = mixer.blend(
            Top,
            meeting=self.meeting,
            attachment=SimpleUploadedFile("test.pdf", b"Test Inhalt"),
        )
        self.std_top = mixer.blend(StandardTop, meetingtype=self.mt1)
        self.function = mixer.blend(Function, meetingtype=self.mt1)
        self.function2 = mixer.blend(Function, meetingtype=self.mt2)
        self.person = mixer.blend(Person, meetingtype=self.mt1)
        self.protokoll = mixer.blend(Protokoll, meeting=self.meeting)
        self.attachment = mixer.blend(
            Attachment,
            meeting=self.meeting,
            attachment=SimpleUploadedFile("test2.pdf", b"Neuer Test Inhalt"),
        )
        self.attendee = mixer.blend(Attendee, meeting=self.meeting)
        fullname = self.protokoll.filepath + "." + self.filetype
        with open(fullname, "a", encoding="UTF-8"):
            pass
        content_type = ContentType.objects.get_for_model(MeetingType)
        self.permission = Permission.objects.get_or_create(
            codename=self.mt1.pk,
            content_type=content_type,
        )[0]
        self.admin_permission = Permission.objects.get_or_create(
            codename=self.mt1.pk + MeetingType.ADMIN,
            content_type=content_type,
        )[0]
        self.permission2 = Permission.objects.get_or_create(
            codename=self.mt2.pk,
            content_type=content_type,
        )[0]
        self.admin_permission2 = Permission.objects.get_or_create(
            codename=self.mt2.pk + MeetingType.ADMIN,
            content_type=content_type,
        )[0]
        self.anonymous_user = AnonymousUser()
        self.logged_in_user = mixer.blend(
            get_user_model(),
            is_registered_user=True,
            is_superuser=False,
            is_staff=False,
        )
        # TODO mixer.RANDOM

        self.admin_user = mixer.blend(
            get_user_model(),
            is_registered_user=True,
            is_superuser=True,
        )
        self.other_user = mixer.blend(
            get_user_model(),
            is_registered_user=True,
            is_superuser=False,
        )
        self.prepared = True

    def prepare_args(self):
        if self.use_person:
            args = [self.mt1.pk, self.person.pk] + self.args
        elif self.use_func:
            args = [self.mt1.pk, self.function.pk] + self.args
        elif self.use_attendee:
            args = [self.mt1.pk, self.meeting.pk, self.attendee.pk] + self.args
        elif self.use_attachment:
            args = [self.mt1.pk, self.meeting.pk, self.attachment.pk] + self.args
        elif self.use_std_top:
            args = [self.mt1.pk, self.std_top.pk] + self.args
        elif self.use_top:
            args = [self.mt1.pk, self.meeting.pk, self.top.pk] + self.args
        elif self.use_meeting:
            args = [self.mt1.pk, self.meeting.pk] + self.args
        elif self.use_mt:
            args = [self.mt1.pk] + self.args
        else:
            args = self.args
        url = self.url.format(*args)
        if self.redirect_url is not None:
            if not self.use_mt and self.use_mt_for_redirect:
                t_args = [self.mt1.pk] + self.args
            elif not self.use_meeting and self.use_meeting_for_redirect:
                t_args = [self.mt1.pk, self.meeting.pk] + self.args
            else:
                t_args = args
            redirect_url = self.redirect_url.format(*t_args)
        else:
            redirect_url = None
        return args, url, redirect_url

    def request_url(self, user, check_result):
        args, url, redirect_url = self.prepare_args()
        client = Client()
        if not isinstance(user, AnonymousUser):
            client.force_login(user)
        check_result(url, redirect_url, lambda _: client.get(url), [])

    def call_view(self, user, check_result):
        if not self.test_view:
            return
        args, url, redirect_url = self.prepare_args()
        req = RequestFactory().get(url)
        req.user = user
        check_result(url, redirect_url, self.view, req, *args)

    def test_anonymous_public(self):
        if self.anonymous_public is None:
            return
        self.mt1.public = True
        self.mt1.save()
        self.request_url(self.anonymous_user, self.anonymous_public)

    def test_anonymous_not_public(self):
        if self.anonymous_not_public is None:
            return
        self.request_url(self.anonymous_user, self.anonymous_not_public)

    def test_logged_in_public(self):
        if self.logged_in_public is None:
            return
        self.mt1.public = True
        self.mt1.save()
        self.request_url(self.logged_in_user, self.logged_in_public)

    def test_logged_in_with_rights(self):
        if self.logged_in_with_rights is None:
            return
        self.logged_in_user.user_permissions.add(self.permission)
        self.request_url(self.logged_in_user, self.logged_in_with_rights)

    def test_logged_in_with_admin_rights(self):
        if self.logged_in_with_admin_rights is None:
            return
        self.logged_in_user.user_permissions.add(self.admin_permission)
        self.request_url(self.logged_in_user, self.logged_in_with_admin_rights)

    def test_logged_in_without_rights(self):
        if self.logged_in_without_rights is None:
            return
        self.request_url(self.logged_in_user, self.logged_in_without_rights)

    def test_logged_in_sitzungsleitung(self):
        if self.logged_in_sitzungsleitung is None:
            return
        self.meeting.sitzungsleitung = self.logged_in_user
        self.meeting.save()
        self.request_url(self.logged_in_user, self.logged_in_sitzungsleitung)

    def test_logged_in_protokollant(self):
        if self.logged_in_protokollant is None:
            return
        self.meeting.minute_takers.clear()
        self.meeting.minute_takers.add(self.logged_in_user)
        self.meeting.save()
        self.request_url(self.logged_in_user, self.logged_in_protokollant)

    def test_admin_public(self):
        if self.admin_public is None:
            return
        self.mt1.public = True
        self.mt1.save()
        self.request_url(self.admin_user, self.admin_public)

    def test_admin_not_public(self):
        if self.admin_not_public is None:
            return
        self.request_url(self.admin_user, self.admin_not_public)

    def test_anonymous_public_view(self):
        if self.anonymous_public is None:
            return
        self.mt1.public = True
        self.mt1.save()
        self.call_view(self.anonymous_user, self.anonymous_public)

    def test_anonymous_not_public_view(self):
        if self.anonymous_not_public is None:
            return
        self.call_view(self.anonymous_user, self.anonymous_not_public)

    def test_logged_in_public_view(self):
        if self.logged_in_public is None:
            return
        self.mt1.public = True
        self.mt1.save()
        self.call_view(self.logged_in_user, self.logged_in_public)

    def test_logged_in_with_rights_view(self):
        if self.logged_in_with_rights is None:
            return
        self.logged_in_user.user_permissions.add(self.permission)
        self.call_view(self.logged_in_user, self.logged_in_with_rights)

    def test_logged_in_with_admin_rights_view(self):
        if self.logged_in_with_admin_rights is None:
            return
        self.logged_in_user.user_permissions.add(self.admin_permission)
        self.call_view(self.logged_in_user, self.logged_in_with_admin_rights)

    def test_logged_in_without_rights_view(self):
        if self.logged_in_without_rights is None:
            return
        self.call_view(self.logged_in_user, self.logged_in_without_rights)

    def test_logged_in_sitzungsleitung_view(self):
        if self.logged_in_sitzungsleitung is None:
            return
        self.meeting.sitzungsleitung = self.logged_in_user
        self.meeting.save()
        self.call_view(self.logged_in_user, self.logged_in_sitzungsleitung)

    def test_logged_in_protokollant_view(self):
        if self.logged_in_protokollant is None:
            return
        self.meeting.minute_takers.clear()
        self.meeting.minute_takers.add(self.logged_in_user)
        self.meeting.save()
        self.call_view(self.logged_in_user, self.logged_in_protokollant)

    def test_admin_public_view(self):
        if self.admin_public is None:
            return
        self.mt1.public = True
        self.mt1.save()
        self.call_view(self.admin_user, self.admin_public)

    def test_admin_not_public_view(self):
        if self.admin_not_public is None:
            return
        self.call_view(self.admin_user, self.admin_not_public)

    def pad_test(self):
        return lambda *args, **kwargs: self.meeting.meetingtype.pad


class AbstractTestWrongMTView(AbstractTestView):
    def prepare_variables(self):
        super().prepare_variables()
        self.meeting.meetingtype = self.mt2
        self.meeting.save()


class AbstractTestImportedView(AbstractTestView):
    def prepare_variables(self):
        super().prepare_variables()
        self.meeting.imported = True
        self.meeting.save()
