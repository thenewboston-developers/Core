Local development environment setup (for Windows)
=================================================

This section describes how to setup development environment for Windows (tested on Windows 10 specifically).

This guide will use Widows Subsystem for Linux (WSL) to get the development environment running on Windows.

IMPORTANT: After the setup is complete, refer to https://code.visualstudio.com/docs/remote/wsl on how to use VS Code
with WSL.

Initial setup
+++++++++++++
Once initial setup is done only corresponding `Update`_ section should be performed to get the latest version for
development.

#. Install Windows Subsystem for Linux (WSL)

   As described on https://docs.microsoft.com/en-us/windows/wsl/install
   run Windows Powershell as administrator and run::
    wsl --install

   Restart system after this

   Then enable WSL by running Powershell as Administrator and run the command::
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

   Just to be safe, restart system again

#. Install Ubuntu environment on Windows

   Search Microsoft store for Ubuntu and install it (Login not required)

#. Search for Ubuntu in taskbar or open up a command prompt and type `ubuntu`. This should open up an Ubuntu terminal.

   Run the rest of the commands in the ubuntu terminal.

#. Install prerequisites (
   as prescribed at https://github.com/pyenv/pyenv/wiki/Common-build-problems and some other)::

    # TODO(dmu) MEDIUM: Remove dependencies that are not really needed
    # TODO(dmu) MEDIUM: These dependencies seem to be candidates for removal: tk-dev wget curl llvm
    sudo apt update && \
    apt install git make build-essential libssl-dev zlib1g-dev libbz2-dev \
                libreadline-dev libsqlite3-dev libncurses5-dev \
                libncursesw5-dev xz-utils libffi-dev liblzma-dev \
                python-openssl libpq-dev

#. Install Docker according to https://docs.docker.com/engine/install/ubuntu/
   (known working: Docker version 20.10.14, build a224086)

#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit  # you may actually need to reboot for group membership to take effect

#. Install Docker Compose according to https://docs.docker.com/compose/install/
   (known working: Docker Compose version v2.4.1)

#. Clone the repository::

    git clone git@github.com:thenewboston-developers/Core.git

#. [if you have not configured it globally] Configure git::

    git config user.name 'Firstname Lastname'
    git config user.email 'youremail@youremail_domain.com'

#. Ensure you have Python 3.10.x installed and it will be used for running the project (you can do it with optional
    steps below)

#. [Optional] Install Python 3.10.x with ``pyenv``

    #. Install and configure `pyenv` according to
       https://github.com/pyenv/pyenv#basic-github-checkout

    #. Install Python 3.10.4::

        pyenv install 3.10.4
        pyenv local 3.10.4 # run from the root of this repo (`.python-version` file should appear)

#. Install Poetry::

    export PIP_REQUIRED_VERSION=22.0.4
    pip install pip==${PIP_REQUIRED_VERSION} && \
    pip install virtualenvwrapper && \
    pip install poetry==1.1.13 && \
    poetry config virtualenvs.path ${HOME}/.virtualenvs && \
    poetry run pip install pip==${PIP_REQUIRED_VERSION}

#. Setup local configuration for running code on host::

    mkdir -p local && \
    cp core/config/settings/templates/settings.dev.py ./local/settings.dev.py && \
    cp core/config/settings/templates/settings.unittests.py ./local/settings.unittests.py

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

Run dockerized
++++++++++++++

#. Run dockerized::

    make run-dockerized

Development tools
+++++++++++++++++

#. Make migrations::

    make migrations

This is a technical last line to serve as `end-of-file-fixer` workaround.
