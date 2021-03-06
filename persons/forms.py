from django import forms
from django.db.models import Max
from django.utils.translation import gettext_lazy as _

from .models import Attendee, Function, Person


class SelectPersonForm(forms.Form):
    person_label = forms.CharField(
        label=_("Person suchen"),
        widget=forms.TextInput(attrs={"size": 80}),
        required=False,
    )
    person = forms.ModelChoiceField(
        queryset=None,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        persons = kwargs.pop("persons")
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = persons


class EditAttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ["functions"]
        widgets = {
            "functions": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")

        super().__init__(*args, **kwargs)

        functions = self.meetingtype.function_set.order_by(
            "sort_order",
            "name",
        )
        self.fields["functions"].queryset = functions


class AddPersonForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ["meetingtype", "version"]
        widgets = {
            "functions": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")

        super().__init__(*args, **kwargs)

        functions = self.meetingtype.function_set.order_by(
            "sort_order",
            "name",
        )
        self.fields["functions"].queryset = functions
        if not self.meetingtype.attendance_with_func or not functions:
            self.fields["functions"].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(False)

        instance.meetingtype = self.meetingtype

        if commit:
            instance.save()

        if self.meetingtype.attendance_with_func:
            self.save_m2m()

        return instance


class AddFunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        exclude = ["sort_order", "meetingtype"]

    def __init__(self, *args, **kwargs):
        self.meetingtype = kwargs.pop("meetingtype")

        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(False)

        instance.meetingtype = self.meetingtype
        maximum = self.meetingtype.function_set.aggregate(
            Max("sort_order"),
        )["sort_order__max"]
        if maximum is None:
            maximum = -1
        instance.sort_order = maximum + 1

        if commit:
            instance.save()

        self.save_m2m()

        return instance


class EditFunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        exclude = ["sort_order", "meetingtype"]
