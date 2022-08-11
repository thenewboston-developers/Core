import logging
import re
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.utils import timezone as django_timezone

from core.core.utils.cryptography import is_signature_valid

TOKEN_RE = re.compile(
    r'^(?P<account_number>[0-9a-f]{64})\$(?P<iso_formatted_datetime>.+?)\$(?P<signature>[0-9a-f]{128})$'
)

logger = logging.getLogger(__name__)


def authenticate(token):
    match = TOKEN_RE.match(token)
    if not match:
        logger.warning(
            'Invalid Authorization token format. Expected: {account_number}${iso_formatted_datetime}${signature}'
        )
        return None

    account_number = match.group('account_number')
    iso_formatted_datetime = match.group('iso_formatted_datetime')
    if not is_signature_valid(iso_formatted_datetime.encode('latin1'), account_number, match.group('signature')):
        logger.warning('Invalid token signature')
        return None

    try:
        moment = datetime.fromisoformat(iso_formatted_datetime)
    except ValueError:
        logger.warning('Invalid token datetime')
        return None

    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)

    if django_timezone.now() - moment > timedelta(seconds=settings.STOKEN_EXPIRATION_SECONDS):
        logger.warning('Token has expired')
        return None

    return account_number
