import pytest
from model_bakery import baker


@pytest.fixture
def sender_account_number():
    return 'a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f'


@pytest.fixture
def recipient_account_number():
    return 'dd8a4c42ece012b528dda5f469a4706d24459e2eee5a867ff5394cf869466bbe'


@pytest.fixture
def sender_account(sender_account_number, db):
    return baker.make('accounts.Account', account_number=sender_account_number, balance=20000)


@pytest.fixture
def recipient_account(sender_account_number, db):
    return baker.make('accounts.Account', account_number=sender_account_number, balance=30000)
