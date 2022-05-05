import pytest
from django.core.exceptions import ValidationError

from core.config.models import Config, get_value


@pytest.mark.django_db
def test_one_config_instance_is_created_with_default_values():
    assert Config.objects.count() == 1
    obj = Config.objects.get()
    assert obj
    assert obj.transaction_fee == 1
    assert obj.owner is None


@pytest.mark.django_db
def test_cannot_add_more_than_one_config_instance():
    assert Config.objects.count() == 1
    extra_obj = Config()
    with pytest.raises(ValidationError, match='Only one config instance is allowed'):
        extra_obj.save()


@pytest.mark.django_db
def test_get_value():
    assert get_value('owner') is None
    assert get_value('transaction_fee') == 1
