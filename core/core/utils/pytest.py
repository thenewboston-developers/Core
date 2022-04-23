import os
import sys


def is_pytest_running():
    # TODO(dmu) MEDIUM: Implement a better way of detecting pytest
    return os.getenv('PYTEST_RUNNING') == 'true' or os.path.basename(sys.argv[0]) in ('pytest', 'py.test')
