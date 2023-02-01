Local development environment setup for MacOS
=============================================

This section describes how to setup development environment for MacOS systems (tested on MacOS BigSur Apple M1 chip).

Initial setup
+++++++++++++
Once initial setup is done only corresponding `Update`_ section should be performed to get the latest version for
development.

#. Install brew::

   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

#. Install prerequisites (as prescribed at https://github.com/pyenv/pyenv/wiki/Common-build-problems and some other)::

    # TODO(dmu) MEDIUM: Remove dependencies that are not really needed
    # TODO(dmu) MEDIUM: These dependencies seem to be candidates for removal: tk-dev wget curl llvm
    brew install openssl readline sqlite3 xz zlib tcl-tk postgresql

#. Install https://docs.docker.com/desktop/mac/install/
   (installs with docker compose plugin built-in)

#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit  # you may actually need to reboot for group membership to take effect

#. Clone the repository::

    git clone https://github.com/thenewboston-developers/Core.git

#. [if you have not configured it globally] Configure git::

    git config user.name 'Firstname Lastname'
    git config user.email 'youremail@youremail_domain.com'

#. Ensure you have Python 3.10.x installed and it will be used for running the project (you can
   do it with optional steps below)
#. [Optional] Install Python 3.10.x with ``pyenv``

    #. Install and configure `pyenv` according to https://github.com/pyenv/pyenv#basic-github-checkout

    #. Install Python 3.10.4::

        pyenv install 3.10.4
        pyenv local 3.10.4 # run from the root of this repo (`.python-version` file should appear)

#. Install Poetry::

    export PIP_REQUIRED_VERSION=23.0
    pip install pip==${PIP_REQUIRED_VERSION} && \
    pip install virtualenvwrapper && \
    pip install poetry==1.3.2 && \
    poetry config virtualenvs.path ${HOME}/.virtualenvs && \
    poetry run pip install pip==${PIP_REQUIRED_VERSION}

#. Setup local configuration for running code on host::

    mkdir -p local && \
    cp core/project/settings/templates/settings.dev.py ./local/settings.dev.py && \
    cp core/project/settings/templates/settings.unittests.py ./local/settings.unittests.py

    # Edit files if needed
    vim ./local/settings.dev.py
    vim ./local/settings.unittests.py

#. Install dependencies, run migrations, etc by doing `Update`_ section steps

#. Create superuser::

    make superuser

Update
++++++
#. (in a separate terminal) Run dependency services::

    make up-dependencies-only

#. Update::

    make update

Run quality assurance tools
+++++++++++++++++++++++++++

#. Lint::

    make lint

Run
+++

#. (in a separate terminal) Run only dependency services with Docker::

    make up-dependencies-only

#. (in a separate terminal) Run server::

    make run-server

Development tools
+++++++++++++++++

#. Make migrations::

    make migrations

This is a technical last line to serve as `end-of-file-fixer` workaround.
