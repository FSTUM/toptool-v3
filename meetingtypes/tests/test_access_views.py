from django.contrib.auth import views as auth_views

from toptool.tests.test_access_views import (
    AbstractTestView,
    accessible,
    not_found,
    permission_denied,
    redirect_to_login,
    redirect_to_url,
)

from .. import feeds, views

# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init


class TestLoginView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/login/"
        self.view = auth_views.LoginView.as_view()
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = accessible
        self.logged_in_public = accessible  # TODO not_found
        self.logged_in_with_rights = accessible  # TODO not_found
        self.logged_in_with_admin_rights = accessible  # TODO not_found
        self.logged_in_without_rights = accessible  # TODO not_found
        self.admin_public = accessible  # TODO not_found
        self.admin_not_public = accessible  # TODO not_found


class TestLogoutView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/logout/"
        self.view = auth_views.LogoutView.as_view()
        self.test_view = False
        self.use_mt = False
        self.use_meeting = False
        self.redirect_url = "/"

        self.anonymous_public = redirect_to_url  # TODO redirect_to_login
        self.anonymous_not_public = redirect_to_url  # TODO redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url
        self.logged_in_without_rights = redirect_to_url
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url


class TestOwnMTsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/overview/"
        self.view = views.list_meetingtypes
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.logged_in_user.user_permissions.add(self.permission)
        self.logged_in_user.user_permissions.add(self.permission2)


class TestOwnMTsOnlyOneView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/overview/"
        self.view = views.list_meetingtypes
        self.use_mt = False
        self.use_meeting = False
        self.use_mt_for_redirect = True
        self.redirect_url = "/{}/"

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = redirect_to_url
        self.logged_in_without_rights = redirect_to_url
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.logged_in_user.user_permissions.add(self.permission)


class TestAllMTsView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/meetingtype/all/"
        self.view = views.list_meetingtypes_admin
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login  # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login  # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login  # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login  # TODO permission_denied
        self.admin_public = redirect_to_login  # TODO accessible
        self.admin_not_public = redirect_to_login  # TODO accessible


class TestAddMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/meetingtype/add/"
        self.view = views.add_meetingtype
        self.use_mt = False
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login  # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login  # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login  # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login  # TODO permission_denied
        self.admin_public = redirect_to_login  # TODO accessible
        self.admin_not_public = redirect_to_login  # TODO accessible


class TestViewMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/"
        self.view = views.view_meetingtype
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied  # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestEditMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/meetingtype/edit/{}/"
        self.view = views.edit_meetingtype
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = permission_denied
        self.logged_in_with_rights = permission_denied
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestDeleteMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/meetingtype/delete/{}/"
        self.view = views.del_meetingtype
        self.use_meeting = False

        self.anonymous_public = redirect_to_login
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_login  # TODO permission_denied
        self.logged_in_with_rights = redirect_to_login  # TODO permission_denied
        self.logged_in_with_admin_rights = redirect_to_login  # TODO permission_denied
        self.logged_in_without_rights = redirect_to_login  # TODO permission_denied
        self.admin_public = redirect_to_login  # TODO accessible
        self.admin_not_public = redirect_to_login  # TODO accessible


class TestUpcomingMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/upcoming/"
        self.view = views.upcoming_meetings
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied  # TODO accessible
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible


class TestIcalMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/ical/{}/"
        self.view = feeds.MeetingFeed()
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = accessible
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = accessible
        self.logged_in_without_rights = accessible
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_args(self):
        self.args = [str(self.mt1.ical_key)]
        return super().prepare_args()


class TestIcalMTNoIcalKeyView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/ical/{}/"
        self.view = feeds.MeetingFeed()
        self.use_meeting = False

        self.anonymous_public = not_found
        self.anonymous_not_public = not_found
        self.logged_in_public = not_found
        self.logged_in_with_rights = not_found
        self.logged_in_with_admin_rights = not_found
        self.logged_in_without_rights = not_found
        self.admin_public = not_found
        self.admin_not_public = not_found

    def prepare_args(self):
        self.args = [self.mt1.ical_key]
        return super().prepare_args()

    def prepare_variables(self):
        super().prepare_variables()
        self.mt1.ical_key = None
        self.mt1.save()


class TestViewArchiveMTView2(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/archive/{}/"
        self.view = views.view_meetingtype_archive
        self.args = [2011]
        self.redirect_url = "/{}/"
        self.use_meeting = False


class TestViewArchiveMTView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/archive/{}/"
        self.view = views.view_meetingtype_archive
        self.args = [2011]
        self.redirect_url = "/{}/"
        self.use_meeting = False

        self.anonymous_public = accessible
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = accessible
        self.logged_in_with_rights = accessible
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.admin_public = accessible
        self.admin_not_public = accessible

    def prepare_variables(self):
        super().prepare_variables()
        self.meeting.time = self.meeting.time.replace(year=2011)
        self.meeting.save()


class TestViewArchiveMTWrongYearView(AbstractTestView):
    def setup_method(self):
        super().setup_method()
        self.url = "/{}/archive/{}/"
        self.view = views.view_meetingtype_archive
        self.args = [2011]
        self.redirect_url = "/{}/"
        self.use_meeting = False

        self.anonymous_public = redirect_to_url
        self.anonymous_not_public = redirect_to_login
        self.logged_in_public = redirect_to_url
        self.logged_in_with_rights = redirect_to_url
        self.logged_in_with_admin_rights = permission_denied
        self.logged_in_without_rights = permission_denied
        self.admin_public = redirect_to_url
        self.admin_not_public = redirect_to_url

    def prepare_variables(self):
        super().prepare_variables()
        self.meeting.time = self.meeting.time.replace(year=2012)
        self.meeting.save()
