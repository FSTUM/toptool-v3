import os.path
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.error import URLError
from uuid import UUID

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import Template
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from py_etherpad import EtherpadLiteClient

from meetings.models import Meeting
from toptool.utils.files import prep_file
from toptool.utils.helpers import get_meeting_or_404_on_validation_error
from toptool.utils.permission import at_least_minute_taker, auth_login_required, require
from toptool.utils.shortcuts import render, send_mail_form
from toptool.utils.typing import AuthWSGIRequest

from .forms import AttachmentForm, PadForm, ProtokollForm, TemplatesForm
from .models import Attachment, Protokoll, protokoll_path


@auth_login_required()
def templates(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Downloads an empty or filled template for a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung and protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)

    protokoll: Optional[Protokoll] = _get_protokoll(meeting)

    last_edit_in_pad_datetime: Optional[datetime]
    last_edit_in_pad_datetime, pad_client = _get_pad_details(meeting)
    last_edit_in_file_datetime: Optional[datetime]
    last_edit_in_file_datetime, __ = _get_last_edit_of_file_datetime_and_t2t(protokoll)
    initial_source: str = _get_initial_source(
        last_edit_in_file_datetime,
        last_edit_in_pad_datetime,
    )

    os_family: str = "unix"
    with suppress(AttributeError):
        if "Windows" in request.user_agent.os.family:  # type: ignore
            os_family = "win"
    form = TemplatesForm(
        request.POST or None,
        last_edit_pad=last_edit_in_pad_datetime,
        last_edit_file=last_edit_in_file_datetime,
        initial={
            "line_breaks": os_family,
            "source": initial_source,
        },
    )
    if form.is_valid():
        text = None
        source = form.cleaned_data["source"]
        if source == "pad" and meeting.meetingtype.pad and meeting.pad:
            try:
                if not pad_client:
                    raise URLError("pad_client not given")
                text = pad_client.getText(meeting.pad)["text"]
            except (URLError, KeyError, ValueError):
                messages.error(
                    request,
                    _("Interner Server Fehler: Pad nicht erreichbar."),
                )
        elif source == "file" and protokoll and protokoll.t2t:
            with open(protokoll.t2t.path, "r", encoding="UTF-8") as file:
                text = file.read()
        elif source == "template":
            text_template = get_template("protokolle/vorlage.t2t")
            text_context = {
                "meeting": meeting,
                "tops_with_id": meeting.tops_with_id,
            }
            text = text_template.render(text_context)

        if text:
            return _convert_text_to_attachment(
                form.cleaned_data["line_breaks"],
                meeting,
                text,
            )

    context = {
        "meeting": meeting,
        "last_edit_file": last_edit_in_file_datetime,
        "last_edit_pad": last_edit_in_pad_datetime,
        "form": form,
    }
    return render(request, "protokolle/templates.html", context)


def _convert_text_to_attachment(
    line_break: str,
    meeting: Meeting,
    text: str,
) -> HttpResponse:
    if line_break == "win":
        text = text.replace("\n", "\r\n")
    response = HttpResponse(content_type="text/text")
    filename = f"protokoll_{meeting.time.year:04}_{meeting.time.month:02}_{meeting.time.day:02}.txt"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    response.write(text)
    return response


@auth_login_required()
def view_pad(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Opens the template in etherpad.

    @permission: allowed only by meetingtype-admin, sitzungsleitung and protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)

    if not meeting.meetingtype.pad:  # meetingtype.protokoll is required in _get_protokoll
        raise Http404

    protokoll: Optional[Protokoll] = _get_protokoll(meeting)

    pad_client = EtherpadLiteClient(settings.ETHERPAD_APIKEY, settings.ETHERPAD_API_URL)
    try:
        group_id = pad_client.createGroupIfNotExistsFor(groupMapper=meeting.pk)["groupID"]
        if not meeting.pad:
            text: Optional[str] = _generate_text_if_not_present(meeting, protokoll)
            name = "protokoll"
            pad_client.createGroupPad(group_id, name, text)
            meeting.pad = f"{group_id}${name}"
            meeting.save()
        session_id: Optional[str] = _generate_etherpad_session_id(request, group_id, pad_client)
        url: Optional[str] = settings.ETHERPAD_PAD_URL
    except (URLError, ValueError):
        url = None
        session_id = None

    form = None
    if url:

        last_edit_in_file_datetime: Optional[datetime]
        last_edit_in_file_datetime, __ = _get_last_edit_of_file_datetime_and_t2t(protokoll)

        form = PadForm(
            request.POST or None,
            request.FILES or None,
            last_edit_file=last_edit_in_file_datetime,
            initial={
                "source": "file" if last_edit_in_file_datetime else "upload",
            },
        )
        if form.is_valid():
            text = None
            source = form.cleaned_data["source"]
            if source == "file" and protokoll:
                with open(protokoll.t2t.path, "r", encoding="UTF-8") as file:
                    text = file.read()
            elif source == "upload":
                if "template_file" in request.FILES:
                    text = request.FILES["template_file"].read()
            elif source == "template":
                text_template = get_template("protokolle/vorlage.t2t")
                text_context = {
                    "meeting": meeting,
                    "tops_with_id": meeting.tops_with_id,
                }
                text = text_template.render(text_context)

            try:
                pad_client.setText(meeting.pad, text)
            except (URLError, ValueError):
                messages.error(
                    request,
                    _(
                        "Interner Server Fehler: Text kann nicht ins Pad geladen werden werden.",
                    ),
                )
            else:
                return redirect("protokolle:view_pad", meeting.pk)

    context = {
        "meeting": meeting,
        "url": url,
        "form": form,
    }
    response = render(request, "protokolle/pad.html", context)
    if session_id:
        response.set_cookie(
            "sessionID",
            session_id,
            domain=settings.ETHERPAD_DOMAIN,
        )
    return response


def _generate_etherpad_session_id(request: AuthWSGIRequest, group_id: str, pad_client: EtherpadLiteClient) -> str:
    author_id = pad_client.createAuthorIfNotExistsFor(request.user.username, request.user.first_name)["authorID"]
    valid_until = datetime.now() + timedelta(hours=7)
    valid_until_timestamp = int(valid_until.timestamp())
    return pad_client.createSession(group_id, author_id, valid_until_timestamp)["sessionID"]  # type: ignore


def _generate_text_if_not_present(meeting: Meeting, protokoll: Optional[Protokoll]) -> str:
    if protokoll:
        with open(protokoll.t2t.path, "r", encoding="UTF-8") as file:
            return file.read()
    else:
        text_template: Template = get_template("protokolle/vorlage.t2t")
        tops = meeting.tops_with_id
        context = {
            "meeting": meeting,
            "tops": tops,
        }
        return text_template.render(context)  # type: ignore


def _get_last_edit_of_file_datetime_and_t2t(
    protokoll: Optional[Protokoll],
) -> tuple[Optional[datetime], Any]:
    if not protokoll or not protokoll.t2t:
        return None, None
    protokoll_edit_timestamp = os.path.getmtime(protokoll.t2t.path)
    return datetime.fromtimestamp(protokoll_edit_timestamp), protokoll.t2t


def _get_initial_source(
    last_edit_in_file: Optional[datetime],
    last_edit_in_pad: Optional[datetime],
    upload: bool = False,
) -> str:
    if last_edit_in_pad:
        last_edit_was_in_file = last_edit_in_file and last_edit_in_pad < last_edit_in_file
        if last_edit_in_file and last_edit_was_in_file:
            return "file"
        return "pad"
    if last_edit_in_file:
        return "file"
    if upload:
        return "upload"
    return "template"


def _get_pad_details(
    meeting: Meeting,
) -> tuple[Optional[datetime], Optional[EtherpadLiteClient]]:
    if not (meeting.meetingtype.pad and meeting.pad):
        return None, None
    pad_client = EtherpadLiteClient(settings.ETHERPAD_APIKEY, settings.ETHERPAD_API_URL)
    try:
        last_edit_timestamp = pad_client.getLastEdited(meeting.pad)["lastEdited"] / 1000
        last_edit_pad = datetime.fromtimestamp(last_edit_timestamp)
        return last_edit_pad, pad_client
    except (URLError, KeyError, ValueError):
        return None, pad_client


@login_required
def show_protokoll(request: WSGIRequest, meeting_pk: UUID, filetype: str) -> HttpResponse:
    """
    Shows the protokoll of a given meeting by type.

    @permission: allowed only for logged-in users with
        a) permission for the meetingtype or
        b) protokoll is publicly available
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @param filetype: filetype of the requested protokoll. can be "html", "pdf", "txt"
    @return: a HttpResponse
    """
    protokoll: Protokoll = get_object_or_404(Protokoll, meeting=meeting_pk)
    meeting: Meeting = protokoll.meeting

    # validity checks
    if filetype not in ["html", "pdf", "txt"]:
        raise Http404("Unsupported Filetype")
    if not meeting.meetingtype.protokoll:
        raise Http404

    # permission checks
    publicly_accessible = meeting.meetingtype.public and protokoll.published and protokoll.approved
    if not publicly_accessible:
        user_has_special_access = (
            request.user.has_perm(meeting.meetingtype.admin_permission)
            or request.user == meeting.sitzungsleitung
            or request.user in meeting.minute_takers.all()
        )
        if not user_has_special_access:
            raise Http404
        if not request.user.has_perm(meeting.meetingtype.access_permission):
            raise PermissionDenied

    # generate_protocol_response
    filetype_lut = {
        "html": HttpResponse(),
        "txt": HttpResponse(content_type="text/plain"),
        "pdf": HttpResponse(content_type="application/pdf"),
    }
    response = filetype_lut[filetype]
    with open(protokoll.filepath + "." + filetype, "rb") as file:
        response.write(file.read())
    return response


@auth_login_required()
def edit_protokoll(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Edits/adds the protokoll of a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung and protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)
    protokoll: Optional[Protokoll] = _get_protokoll(meeting)

    last_edit_in_pad_datetime: Optional[datetime]
    last_edit_in_pad_datetime, pad_client = _get_pad_details(meeting)

    last_edit_in_file_datetime: Optional[datetime]
    last_edit_in_file_datetime, t2t = _get_last_edit_of_file_datetime_and_t2t(protokoll)

    initial_source = _get_initial_source(
        last_edit_in_pad_datetime,
        last_edit_in_file_datetime,
        upload=True,
    )

    initial = _generate_initial_form_data(initial_source, meeting, protokoll)

    users = (
        get_user_model()
        .objects.filter(
            Q(user_permissions=meeting.meetingtype.get_permission())
            | Q(groups__permissions=meeting.meetingtype.get_permission()),
        )
        .distinct()
        .order_by("first_name", "last_name", "username")
    )

    form = ProtokollForm(
        request.POST or None,
        request.FILES or None,
        instance=protokoll,
        initial=initial,
        users=users,
        meeting=meeting,
        t2t=t2t,
        last_edit_pad=last_edit_in_pad_datetime,
        last_edit_file=last_edit_in_file_datetime,
    )
    if form.is_valid():
        text = None
        source = form.cleaned_data["source"]
        if source == "pad" and meeting.meetingtype.pad and meeting.pad:
            text = _get_text_from_etherpad(request, meeting, pad_client)
        elif source == "file" and t2t:
            text = "__file__"
        elif source == "upload" and "protokoll" in request.FILES:
            try:
                text = request.FILES["protokoll"].read().decode("utf8")
            except UnicodeDecodeError:
                messages.error(
                    request,
                    _("Encoding-Fehler: Die Protokoll-Datei ist nicht UTF-8 kodiert."),
                )

        if text:
            form.save()
            if not meeting.sitzungsleitung:
                meeting.sitzungsleitung = form.cleaned_data["sitzungsleitung"]
            if not meeting.minute_takers.exists():
                meeting.minute_takers.add(request.user)
            meeting.save()
            if text != "__file__":
                _save_text_to_t2t_file(meeting, text)

            response: Optional[HttpResponse] = meeting.protokoll.handle_generation(request)
            if response:
                return response

    context = {
        "meeting": meeting,
        "form": form,
    }
    return render(request, "protokolle/edit.html", context)


def _get_text_from_etherpad(
    request: AuthWSGIRequest,
    meeting: Meeting,
    pad_client: EtherpadLiteClient,
) -> Optional[str]:
    try:
        if not pad_client:
            raise URLError("pad_client not given")
        return pad_client.getText(meeting.pad)["text"]  # type: ignore
    except (URLError, KeyError, ValueError):
        messages.error(
            request,
            _("Interner Server Fehler: Pad nicht erreichbar."),
        )
    return None


def _generate_initial_form_data(
    initial_source: str,
    meeting: Meeting,
    protokoll: Optional[Protokoll],
) -> dict[str, Any]:
    initial: dict[str, Any] = {
        "sitzungsleitung": meeting.sitzungsleitung,
        "source": initial_source,
    }
    if not protokoll:
        initial["begin"] = timezone.localtime(meeting.time).timetz()
        initial["end"] = (timezone.localtime(meeting.time) + timedelta(hours=2)).timetz()
    if not meeting.meetingtype.approve:
        initial["approved"] = True
    return initial


def _save_text_to_t2t_file(meeting, text):
    if meeting.protokoll.t2t:
        with open(meeting.protokoll.t2t.path, "w", encoding="UTF-8") as file:
            file.write(text)
    else:
        meeting.protokoll.t2t.save(
            protokoll_path(meeting.protokoll, "protokoll.t2t"),
            ContentFile(text),
        )


def _get_protokoll(meeting: Meeting) -> Optional[Protokoll]:
    if not meeting.meetingtype.protokoll:
        raise Http404
    try:
        return meeting.protokoll
    except Protokoll.DoesNotExist:
        return None


@auth_login_required()
def successful_protokoll_generation(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Notifies the user, that the protokoll of a given meeting has been successfully generated.
    The protokoll can now be published (and optionally send via mail).

    @permission: allowed only by meetingtype-admin, sitzungsleitung and protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)
    if not meeting.meetingtype.protokoll:
        raise Http404

    protokoll: Protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    context = {
        "meeting": meeting,
        "protokoll": protokoll,
    }
    return render(request, "protokolle/successful_protokoll_generation.html", context)


@auth_login_required()
def publish_protokoll(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Publishes the protokoll of a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """
    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    if not meeting.meetingtype.protokoll:
        raise Http404

    protokoll: Protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    if protokoll.published:
        raise Http404

    form = forms.Form(request.POST or None)
    if form.is_valid():
        protokoll.published = True
        protokoll.save()
        return redirect("protokolle:publish_success", meeting.id)

    context = {
        "meeting": meeting,
        "protokoll": protokoll,
        "form": form,
    }
    return render(request, "protokolle/publish.html", context)


@auth_login_required()
def publish_success(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Notifies the user, that the protokoll of a given meeting has been successfully published.
    The protokoll can still be optionally send via mail.

    @permission: allowed only by meetingtype-admin, sitzungsleitung and protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)
    if not meeting.meetingtype.protokoll:
        raise Http404

    protokoll: Protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    if not protokoll.published:
        raise Http404

    context = {
        "meeting": meeting,
        "protokoll": protokoll,
    }
    return render(request, "protokolle/publish_success.html", context)


@auth_login_required()
def delete_protokoll(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Deletes the protokoll of a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied

    if not meeting.meetingtype.protokoll:
        raise Http404

    protokoll: Protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    form = forms.Form(request.POST or None)
    if form.is_valid():
        Protokoll.objects.filter(pk=meeting_pk).delete()
        return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "protokoll": protokoll,
        "form": form,
    }
    return render(request, "protokolle/del.html", context)


@auth_login_required()
def delete_etherpad(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Deletes the etherpad for a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    if not (request.user.has_perm(meeting.meetingtype.admin_permission) or request.user == meeting.sitzungsleitung):
        raise PermissionDenied

    if not (meeting.meetingtype.protokoll and meeting.meetingtype.pad and meeting.pad):
        raise Http404

    pad_client = EtherpadLiteClient(
        settings.ETHERPAD_APIKEY,
        settings.ETHERPAD_API_URL,
    )
    try:
        last_edit_pad: Optional[datetime] = datetime.fromtimestamp(
            pad_client.getLastEdited(meeting.pad)["lastEdited"] / 1000,
        )
    except (URLError, KeyError, ValueError):
        last_edit_pad = None

    form = None
    if last_edit_pad:
        form = forms.Form(request.POST or None)
        if form.is_valid():
            try:
                group_id = pad_client.createGroupIfNotExistsFor(groupMapper=meeting.pk)["groupID"]
                pad_client.deleteGroup(group_id)
            except URLError:
                messages.error(
                    request,
                    _("Interner Server Fehler: Etherpad ist nicht erreichbar."),
                )
            except (KeyError, ValueError):
                messages.error(
                    request,
                    _("Interner Server Fehler: Das Pad konnte nicht gelöscht werden."),
                )
            else:
                meeting.pad = ""
                meeting.save()
                return redirect("meetings:view_meeting", meeting.id)

    context = {
        "meeting": meeting,
        "last_edit_pad": last_edit_pad,
        "form": form,
    }
    return render(request, "protokolle/delpad.html", context)


@auth_login_required()
def send_protokoll(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Sends the protokoll of a given meeting to the meetingtypes mailing list.

    @permission: allowed only by meetingtype-admin, sitzungsleitung, protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)
    if not meeting.meetingtype.send_minutes_enabled:
        raise Http404

    protokoll: Protokoll = get_object_or_404(Protokoll, pk=meeting_pk)

    if not protokoll.published:
        raise Http404

    mail_details: tuple[str, str, str, str] = protokoll.get_mail(request)
    return send_mail_form("protokolle/send_mail.html", request, mail_details, meeting, protokoll)


@auth_login_required()
def attachments(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Adds, edits or removes attachments to the protokoll of a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung or protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)
    require(at_least_minute_taker(request, meeting))

    require(not meeting.imported)
    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    attachment_list = Attachment.objects.filter(meeting=meeting).order_by(
        "sort_order",
        "name",
    )

    form = AttachmentForm(request.POST or None, request.FILES or None, meeting=meeting)
    if form.is_valid():
        form.save()
        return redirect("protokolle:attachments", meeting.id)

    context = {
        "meeting": meeting,
        "attachments": attachment_list,
        "form": form,
    }
    return render(request, "protokolle/attachments.html", context)


@auth_login_required()
def sort_attachments(request: AuthWSGIRequest, meeting_pk: UUID) -> HttpResponse:
    """
    Enables the user to sort the attachments for protokoll of a given meeting.

    @permission: allowed only by meetingtype-admin, sitzungsleitung or protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param meeting_pk: uuid of a Meeting
    @return: a HttpResponse
    """

    meeting: Meeting = get_meeting_or_404_on_validation_error(meeting_pk)

    if not (
        request.user.has_perm(
            meeting.meetingtype.admin_permission,
        )
        or request.user == meeting.sitzungsleitung
        or request.user in meeting.minute_takers.all()
    ):
        raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    if request.method == "POST":
        attachment_list = request.POST.getlist("attachments[]")
        attachment_list = [t for t in attachment_list if t]
        if attachment_list:
            for i, attach in enumerate(attachment_list):
                try:
                    attach_pk = int(attach.partition("_")[2])
                except (ValueError, IndexError):
                    return HttpResponseBadRequest()
                try:
                    attachment: Attachment = Attachment.objects.get(pk=attach_pk)
                except Attachment.DoesNotExist:
                    return HttpResponseBadRequest()
                attachment.sort_order = i
                attachment.save()
            return JsonResponse({"success": True})

    return HttpResponseBadRequest()


@auth_login_required()
def show_attachment(request: AuthWSGIRequest, attachment_pk: int) -> HttpResponse:
    """
    Show a protokoll attachment.

    @permission: allowed only by users with permission for the meetingtype
    @param request: a WSGIRequest by a logged-in user
    @param attachment_pk: id of an Attachment
    @return: a HttpResponse
    """

    attachment: Attachment = get_object_or_404(Attachment, pk=attachment_pk)
    meeting: Meeting = attachment.meeting

    if not request.user.has_perm(meeting.meetingtype.access_permission):
        raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    protokoll: Protokoll = attachment.meeting.protokoll

    if not protokoll.published and not (
        request.user.has_perm(
            meeting.meetingtype.admin_permission,
        )
        or request.user == meeting.sitzungsleitung
        or request.user in meeting.minute_takers.all()
    ):
        raise Http404
    return prep_file(attachment.attachment.path)


@auth_login_required()
def edit_attachment(request: AuthWSGIRequest, attachment_pk: int) -> HttpResponse:
    """
    Edits a protokoll attachment.

    @permission: allowed only by meetingtype-admin, sitzungsleitung or protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param attachment_pk: id of an Attachment
    @return: a HttpResponse
    """

    attachment: Attachment = get_object_or_404(Attachment, pk=attachment_pk)
    meeting: Meeting = attachment.meeting

    if not (
        request.user.has_perm(
            meeting.meetingtype.admin_permission,
        )
        or request.user == meeting.sitzungsleitung
        or request.user in meeting.minute_takers.all()
    ):
        raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    form = AttachmentForm(
        request.POST or None,
        request.FILES or None,
        meeting=meeting,
        instance=attachment,
    )
    if form.is_valid():
        form.save()
        return redirect("protokolle:attachments", meeting.id)

    context = {
        "meeting": meeting,
        "attachment": attachment,
        "form": form,
    }
    return render(request, "protokolle/edit_attachment.html", context)


@auth_login_required()
def del_attachment(request: AuthWSGIRequest, attachment_pk: int) -> HttpResponse:
    """
    Deletes a protokoll attachment.

    @permission: allowed only by meetingtype-admin, sitzungsleitung or protokollant*innen
    @param request: a WSGIRequest by a logged-in user
    @param attachment_pk: id of an Attachment
    @return: a HttpResponse
    """

    attachment: Attachment = get_object_or_404(Attachment, pk=attachment_pk)
    meeting: Meeting = attachment.meeting

    if not (
        request.user.has_perm(
            meeting.meetingtype.admin_permission,
        )
        or request.user == meeting.sitzungsleitung
        or request.user in meeting.minute_takers.all()
    ):
        raise PermissionDenied
    require(not meeting.imported)

    if not meeting.meetingtype.protokoll or not meeting.meetingtype.attachment_protokoll:
        raise Http404

    form = forms.Form(request.POST or None)
    if form.is_valid():
        attachment.delete()
        return redirect("protokolle:attachments", meeting.id)

    context = {
        "meeting": meeting,
        "attachment": attachment,
        "form": form,
    }
    return render(request, "protokolle/delete_attachment.html", context)
