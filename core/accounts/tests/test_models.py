from unittest.mock import patch

from core.accounts.consumers import MessageType
from core.accounts.models import Peer


def test_account_send(recipient_account):
    recipient_account.balance += 3

    with patch('core.accounts.consumers.send') as send_mock:
        recipient_account.save()

    message = {
        'account_number': recipient_account.account_number,
        'balance': recipient_account.balance,
    }
    send_mock.assert_called_once_with(MessageType.UPDATE_ACCOUNT, recipient_account.account_number, message)


def test_peer_to_peer_relationship(sender_account, recipient_account):
    assert not sender_account.allowed_peers.exists()
    assert not sender_account.allowing_peers.exists()
    assert not recipient_account.allowed_peers.exists()
    assert not recipient_account.allowing_peers.exists()

    assert not sender_account.is_mutual_peering(recipient_account.account_number)
    assert not recipient_account.is_mutual_peering(sender_account.account_number)

    Peer.objects.create(allowing_peer=sender_account, allowed_peer=recipient_account)

    assert list(sender_account.allowed_peers.all()) == [recipient_account]
    assert not sender_account.allowing_peers.exists()
    assert not recipient_account.allowed_peers.exists()
    assert list(recipient_account.allowing_peers.all()) == [sender_account]

    assert not sender_account.is_mutual_peering(recipient_account.account_number)
    assert not recipient_account.is_mutual_peering(sender_account.account_number)

    Peer.objects.create(allowing_peer=recipient_account, allowed_peer=sender_account)

    assert list(sender_account.allowed_peers.all()) == [recipient_account]
    assert list(sender_account.allowing_peers.all()) == [recipient_account]
    assert list(recipient_account.allowed_peers.all()) == [sender_account]
    assert list(recipient_account.allowing_peers.all()) == [sender_account]

    assert sender_account.is_mutual_peering(recipient_account.account_number)
    assert recipient_account.is_mutual_peering(sender_account.account_number)
