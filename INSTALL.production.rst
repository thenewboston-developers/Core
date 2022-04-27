Run production Core API
=======================

Common configuration
++++++++++++++++++++

#. Provision target machine of at least these specs: Ubuntu 20.04 64-bit (x86), 1Gb RAM, 16Gb storage
#. Install Docker on target machine according to https://docs.docker.com/engine/install/ubuntu/
   (known working: Docker version 20.10.14, build a224086)
#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit

#. Install Docker Compose  on target machine according to https://docs.docker.com/compose/install/
   (known working: Docker Compose version v2.4.1)

Manual deployment
+++++++++++++++++

#. Prepare github personal access token aka PAT (not github password) - it will be needed to
   access the node docker image
#. Run ``deploy.sh``::

    bash <(wget -qO- https://raw.githubusercontent.com/thenewboston-developers/Core/master/scripts/deploy.sh)

#. Create superuser::

    docker compose exec -it core poetry run python -m core.manage createsuperuser

This is a technical last line to serve as `end-of-file-fixer` workaround.
