import pytest

from core.accounts.models import Account


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
def test_update_account(sender_account, attribute, value, is_success, api_client):
    original_value = getattr(sender_account, attribute)
    assert original_value != value

    payload = {attribute: value}
    response = api_client.patch(f'/api/accounts/{sender_account.account_number}', payload)
    sender_account.refresh_from_db()

    # TODO(dmu) LOW: DRF has an issue of not reporting an error if a read-only field is requested for update
    #                Maybe we should fix it and respond with HTTP400 in such cases
    assert response.status_code == 200
    expected_response_body = {
        'account_number': sender_account.account_number,
        'avatar': sender_account.avatar,
        'balance': sender_account.balance,
        'display_name': sender_account.display_name,
    }
    if is_success:
        assert response.json() == expected_response_body | payload
        assert getattr(sender_account, attribute) == value
    else:
        assert response.json() == expected_response_body
        assert getattr(sender_account, attribute) == original_value


# TODO(dmu) CRITICAL: Disable PUT requests, so balance cannot be updated directly
#                     https://github.com/thenewboston-developers/Core/issues/30


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
