import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestMeeting:
    def test_init(self):
        obj = mixer.blend("persons.Person")
        assert obj.pk not in (None, ""), "Should create a Person instance"
