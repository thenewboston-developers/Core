import pytest

from core.accounts.models import Account
from core.core.utils.collections import remove_keys
from core.core.utils.cryptography import sign_dict


def test_retrieve_account(sender_account, api_client):
    response = api_client.get(f'/api/accounts/{sender_account.account_number}')
    assert response.status_code == 200
    assert response.json() == {
        'account_number': sender_account.account_number,
        'avatar': sender_account.avatar,
        'balance': sender_account.balance,
        'display_name': sender_account.display_name,
    }


@pytest.mark.parametrize(
    'attribute, value, is_success', (
        ('avatar', 'https://example.com/me.jpg', True),
        ('display_name', 'New Name', True),
        ('account_number', '0000000000000000000000000000000000000000000000000000000000000000', False),
        ('balance', 10001, False),
    )
)
def test_update_account(sender_account, sender_key_pair, attribute, value, is_success, api_client):
    original_value = getattr(sender_account, attribute)
    assert original_value != value

    payload = {attribute: value}
    sign_dict(payload, sender_key_pair.private)
    response = api_client.patch(f'/api/accounts/{sender_account.account_number}', payload)
    sender_account.refresh_from_db()

    if is_success:
        assert response.status_code == 200
        expected_response_body = {
            'account_number': sender_account.account_number,
            'avatar': sender_account.avatar,
            'balance': sender_account.balance,
            'display_name': sender_account.display_name,
        }
        assert response.json() == expected_response_body | remove_keys(payload, ('signature',))
        assert getattr(sender_account, attribute) == value
    else:
        assert response.status_code == 400
        assert response.json() == {
            'non_field_errors': [{
                'code': 'invalid',
                'message': f'Readonly field(s): {attribute}'
            }]
        }
        assert getattr(sender_account, attribute) == original_value


def test_cannot_update_account_with_invalid_signature(sender_account, api_client):
    original_value = sender_account.avatar

    payload = {'avatar': 'https://example.com/avatar.jpg', 'signature': '0' * 128}
    response = api_client.patch(f'/api/accounts/{sender_account.account_number}', payload)

    assert response.status_code == 400
    assert response.json() == {'signature': [{'code': 'invalid', 'message': 'Invalid'}]}
    sender_account.refresh_from_db()
    assert sender_account.avatar == original_value


def test_cannot_update_account_without_signature(sender_account, api_client):
    original_value = sender_account.avatar

    payload = {'avatar': 'https://example.com/avatar.jpg'}
    response = api_client.patch(f'/api/accounts/{sender_account.account_number}', payload)

    assert response.status_code == 400
    assert response.json() == {'signature': [{'code': 'invalid', 'message': 'This field is required.'}]}
    sender_account.refresh_from_db()
    assert sender_account.avatar == original_value


def test_cannot_put_account(sender_account, api_client):
    avatar = 'https://example.com/test.jpg'
    display_name = 'New Name'
    assert sender_account.avatar != avatar
    assert sender_account.display_name != display_name
    payload = {
        'avatar': avatar,
        'display_name': display_name,
    }
    response = api_client.put(f'/api/accounts/{sender_account.account_number}', payload)
    sender_account.refresh_from_db()

    assert response.status_code == 405
    assert response.json() == {'code': 'method_not_allowed', 'message': 'Method "PUT" not allowed.'}

    assert sender_account.avatar != avatar
    assert sender_account.display_name != display_name


@pytest.mark.django_db
def test_cannot_create_account(api_client):
    assert not Account.objects.exists()
    payload = {
        'account_number': '0000000000000000000000000000000000000000000000000000000000000000',
        'avatar': 'https://example.com/me.jpg',
        'balance': 1234,
        'display_name': 'Display Name',
    }
    response = api_client.post('/api/accounts', payload)
    assert response.status_code == 404
    assert not Account.objects.exists()
