import pytest

from core.core.utils.cryptography import sign_dict
from core.settings.models import Config


@pytest.mark.django_db
def test_can_get_config(api_client):
    response = api_client.get('/api/config/self')
    assert response.status_code == 200
    assert response.json() == {'owner': None, 'transaction_fee': 1}


@pytest.mark.django_db
def test_cannot_get_config_by_real_identifier(api_client):
    config = Config.objects.get()
    response = api_client.get(f'/api/config/{config.id}')
    assert response.status_code == 404


@pytest.mark.parametrize('attribute, value', (
    ('owner', '1' * 64),
    ('transaction_fee', 10),
))
@pytest.mark.django_db
def test_update_config(sender_key_pair, attribute, value, api_client):
    config = Config.objects.get()
    config.owner = sender_key_pair.public
    config.save()

    assert getattr(config, attribute) != value

    payload = {'account_number': sender_key_pair.public, attribute: value}
    sign_dict(payload, sender_key_pair.private)
    response = api_client.patch('/api/config/self', payload)
    assert response.status_code == 200
    assert response.json().get(attribute) == value

    response = api_client.get('/api/config/self')
    assert response.status_code == 200
    assert response.json().get(attribute) == value

    config.refresh_from_db()
    assert getattr(config, attribute) == value


@pytest.mark.parametrize(
    'owner, expected_response_json', (
        (None, {
            'non_field_errors': [{
                'code': 'invalid',
                'message': 'Owner must be configured.'
            }]
        }),
        ('1' * 64, {
            'account_number': [{
                'code': 'invalid',
                'message': 'Must be owner.'
            }]
        }),
    )
)
@pytest.mark.django_db
def test_cannot_update_config_if_account_number_does_not_match_owner(
    sender_key_pair, owner, expected_response_json, api_client
):
    assert sender_key_pair.public != owner

    config = Config.objects.get()
    config.owner = owner
    config.save()

    assert config.transaction_fee == 1
    payload = {'account_number': sender_key_pair.public, 'transaction_fee': 10}
    sign_dict(payload, sender_key_pair.private)
    response = api_client.patch('/api/config/self', payload)
    assert response.status_code == 400
    assert response.json() == expected_response_json

    config.refresh_from_db()
    assert config.transaction_fee == 1

    assert owner != '2' * 64
    payload = {'account_number': sender_key_pair.public, 'owner': '2' * 64}
    sign_dict(payload, sender_key_pair.private)
    response = api_client.patch('/api/config/self', payload)
    assert response.status_code == 400
    assert response.json() == expected_response_json

    config.refresh_from_db()
    assert config.owner == owner


@pytest.mark.parametrize('transaction_fee', (0, -1))
@pytest.mark.django_db
def test_cannot_update_transaction_fee_to_zero(sender_key_pair, transaction_fee, api_client):
    config = Config.objects.get()
    assert config.transaction_fee != transaction_fee
    assert config.transaction_fee == 1
    config.owner = sender_key_pair.public
    config.save()

    payload = {'account_number': sender_key_pair.public, 'transaction_fee': transaction_fee}
    sign_dict(payload, sender_key_pair.private)
    response = api_client.patch('/api/config/self', payload)
    assert response.status_code == 400
    assert response.json() == {
        'transaction_fee': [{
            'code': 'min_value',
            'message': 'Ensure this value is greater than or equal to 1.'
        }]
    }

    config.refresh_from_db()
    assert config.transaction_fee == 1


@pytest.mark.django_db
def test_cannot_update_config_by_real_identifier(sender_key_pair, api_client):
    config = Config.objects.get()
    assert config.transaction_fee == 1
    config.owner = sender_key_pair.public
    config.save()

    payload = {'account_number': sender_key_pair.public, 'transaction_fee': 4}
    sign_dict(payload, sender_key_pair.private)
    response = api_client.patch(f'/api/config/{config.id}', payload)

    assert response.status_code == 404
    config.refresh_from_db()
    assert config.transaction_fee == 1


def test_cannot_update_config_with_invalid_signature(sender_account, api_client):
    config = Config.objects.get()
    assert config.transaction_fee == 1
    config.owner = sender_account.account_number
    config.save()

    payload = {'account_number': sender_account.account_number, 'transaction_fee': 4, 'signature': '0' * 128}
    response = api_client.patch('/api/config/self', payload)

    assert response.status_code == 400
    assert response.json() == {'signature': [{'code': 'invalid', 'message': 'Invalid.'}]}
    config.refresh_from_db()
    assert config.transaction_fee == 1


def test_cannot_update_config_without_signature(sender_account, api_client):
    config = Config.objects.get()
    assert config.transaction_fee == 1
    config.owner = sender_account.account_number
    config.save()

    payload = {'transaction_fee': 4}
    response = api_client.patch('/api/config/self', payload)

    assert response.status_code == 400
    assert response.json() == {'signature': [{'code': 'invalid', 'message': 'This field is required.'}]}
    config.refresh_from_db()
    assert config.transaction_fee == 1


def test_cannot_put_config(sender_account, api_client):
    config = Config.objects.get()
    assert config.transaction_fee == 1

    payload = {'transaction_fee': 4}
    response = api_client.put('/api/config/self', payload)

    assert response.status_code == 405
    assert response.json() == {'code': 'method_not_allowed', 'message': 'Method "PUT" not allowed.'}

    config.refresh_from_db()
    assert config.transaction_fee == 1


@pytest.mark.django_db
def test_cannot_create_config(api_client):
    assert Config.objects.count() == 1
    payload = {'transaction_fee': 4}
    response = api_client.post('/api/config', payload)
    assert response.status_code == 404
