from datetime import datetime, timedelta

from django.utils import timezone

from core.core.authentication import authenticate
from core.core.utils.cryptography import generate_signature


def test_can_authenticate(sender_key_pair):
    now = timezone.now().isoformat()
    signature = generate_signature(now.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}${now}${signature}'
    assert authenticate(token) == sender_key_pair.public


def test_naive_datetime_authenticate(sender_key_pair):
    now = datetime.utcnow()
    assert now.tzinfo is None
    now_str = now.isoformat()
    signature = generate_signature(now_str.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}${now_str}${signature}'
    assert authenticate(token) == sender_key_pair.public


def test_invalid_token_format_authenticate(sender_key_pair):
    assert authenticate('some token') is None
    assert authenticate('fake$fake') is None


def test_invalid_datetime_authenticate(sender_key_pair):
    now = timezone.now().isoformat()
    signature = generate_signature(now.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}$pokfoijeoif${signature}'
    assert authenticate(token) is None


def test_expired_token_authenticate(sender_key_pair):
    token_time = (timezone.now() - timedelta(seconds=15)).isoformat()
    signature = generate_signature(token_time.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}${token_time}${signature}'
    assert authenticate(token) is None
