import pytest
from model_bakery import baker

from core.config.models import Config
from core.core.utils.cryptography import KeyPair


@pytest.fixture
def sender_key_pair():
    return KeyPair(
        public='eb01f474a637e402b44407f3c1044a0c4b59261515d50be9abd4ee34fcb9075b',
        private='acb34653559abebeabf67e01c89ab5f0859674c8a643b294b9ffc89012ac2e2e'
    )


@pytest.fixture
def sender_account_number(sender_key_pair):
    return sender_key_pair.public


@pytest.fixture
def recipient_key_pair():
    return KeyPair(
        public='6fac7f7e2b90173bfc6ef8ee34f9c92438b5eb8f579ef8d84464b820bbfecfc1',
        private='ecde1ad0e2f1bf6ebf8d409df251bed273601b6d37e615912f11373468fb8a10'
    )


@pytest.fixture
def recipient_account_number(recipient_key_pair):
    return recipient_key_pair.public


@pytest.fixture
def owner_key_pair():
    return KeyPair(
        public='8d215ae8c153ad90cbe089117190e98cc608ddea956f2b3485ab1cb899ea7329',
        private='c1b1195bee12379d96798fc0e498c5b97e6026cc2011ecc9d788470e32c63b42'
    )


@pytest.fixture
def owner_account_number(owner_key_pair):
    return owner_key_pair.public


@pytest.fixture
def sender_account(sender_account_number, db):
    return baker.make('accounts.Account', account_number=sender_account_number, balance=20000)


@pytest.fixture
def recipient_account(recipient_account_number, db):
    return baker.make('accounts.Account', account_number=recipient_account_number, balance=30000)


@pytest.fixture
def owner_account(owner_account_number, db):
    return baker.make('accounts.Account', account_number=owner_account_number, balance=50000)


@pytest.fixture
def owner_account_setting(owner_account_number, db):
    config = Config.objects.get()
    original_value = config.owner
    config.owner = owner_account_number
    config.save()
    yield
    config.owner = original_value
    config.save()
