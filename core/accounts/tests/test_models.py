from unittest.mock import patch

from core.accounts.consumers import MessageType


def test_account_send(recipient_account):
    recipient_account.balance += 3

    with patch('core.accounts.consumers.send') as send_mock:
        recipient_account.save()

    message = {
        'account_number': recipient_account.account_number,
        'balance': recipient_account.balance,
    }
    send_mock.assert_called_once_with(MessageType.UPDATE_ACCOUNT, recipient_account.account_number, message)
