import logging
import re
from datetime import datetime, timedelta, timezone

from channels.middleware import BaseMiddleware
from django.conf import settings
from django.utils import timezone as django_timezone

from core.core.utils.cryptography import is_signature_valid

AUTH_HEADER_RE = re.compile(
    r'SToken (?P<account_number>[0-9a-f]{64})\$(?P<iso_formatted_datetime>.+?)\$(?P<signature>[0-9a-f]{128})'
)

logger = logging.getLogger(__name__)


def authenticate(headers):
    authorization_header = headers.get(b'authorization')
    if not authorization_header:
        logger.info('Authorization HTTP-header is not found')
        return None

    authorization_header_decoded = authorization_header.decode('latin1')
    match = AUTH_HEADER_RE.match(authorization_header_decoded)
    if not match:
        logger.warning(
            'Invalid Authorization HTTP-header format. '
            'Expected: SToken {account_number}${iso_formatted_datetime}${signature}',
        )
        return None

    account_number = match.group('account_number')
    iso_formatted_datetime = match.group('iso_formatted_datetime')
    if not is_signature_valid(iso_formatted_datetime.encode('latin1'), account_number, match.group('signature')):
        logger.warning('Invalid signature in %s', authorization_header_decoded)
        return None

    try:
        moment = datetime.fromisoformat(iso_formatted_datetime)
    except ValueError:
        logger.warning('Invalid datetime in %s', authorization_header_decoded)
        return None

    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)

    if django_timezone.now() - moment > timedelta(seconds=settings.STOKEN_EXPIRATION_SECONDS):
        logger.warning('Token has expired: %s', authorization_header_decoded)
        return None

    return account_number


class SignatureAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        """
        ASGI application; can insert things into the scope and run asynchronous
        code.
        """
        # Documentation says that authentication should be implemented as middleware:
        # https://channels.readthedocs.io/en/latest/topics/authentication.html
        # Therefore we put it here while authorization (which does not allow unauthenticated)
        # is implemented in core.accounts.consumers.AccountConsumer.connect() method
        scope = dict(scope, authenticated_account_number=authenticate(dict(scope['headers'])))
        return await self.inner(scope, receive, send)
