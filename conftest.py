import os

# TODO(dmu) LOW: For some reason pytest does not recognize conftest.py if being placed into `core`
#                package. Fix it.

# Set on the earliest possible moment
os.environ['PYTEST_RUNNING'] = 'true'

from core.accounts.tests.fixtures import *  # noqa: F401, F403, E402
from core.core.tests.fixtures import *  # noqa: F401, F403, E402
