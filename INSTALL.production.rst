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

#. Check that required docker images are available (thenewboston-developers/Core repo maintainer take care of it
   with `<INSTALL.dockerhub.rst>`_ instructions)::

    docker pull thenewboston/core
    docker pull thenewboston/core-reverse-proxy

#. Acquire a domain name and create a DNS record of type A pointing to the target machine public IP-address

Manual deployment
+++++++++++++++++

#. Prepare github personal access token aka PAT (not github password) - it will be needed to
   access the node docker image (description is based on
   https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token ):

    #. Login to your github account (register it if you do not have one)
    #. Verify your email address for github, if it has not been verified yet
    #. In the upper-right corner of any page, click your profile photo, then click Settings ( https://github.com/settings/profile )
    #. In the left sidebar, click <> Developer settings
    #. In the left sidebar, click Personal access tokens ( https://github.com/settings/tokens )
    #. Click "Generate new token"
    #. Fill in "Note" field
    #. Choose "No expiration" in "Expiration" field
    #. Check "read:packages" (Download packages from GitHub Package Registry) in Select Scopes box
    #. Click "Generate token"
    #. Copy your personal access token (PAT). You will not be able to see it again!

#. Run ``deploy.sh``::

    bash <(wget -qO- https://raw.githubusercontent.com/thenewboston-developers/Core/master/scripts/deploy.sh)

#. Create superuser::

    docker compose exec -it core poetry run python -m core.manage createsuperuser

Configure continuous deployment
+++++++++++++++++++++++++++++++

#. Create deploy ssh key on target machine::

    # Use empty pass phrase
    ssh-keygen -f ~/.ssh/github
    cat ~/.ssh/github.pub >> ~/.ssh/authorized_keys

#. Create github repository secrets::

    CONTINUOUS_DEPLOYMENT_ENABLED=True
    DEPLOY_SSH_KEY=<content of ~/.ssh/github>
    DEPLOY_SSH_HOST=<IP-address or domain name of target machine>
    DEPLOY_SSH_USER=<username that has the corresponding public in ~/authorized_keys>

This is a technical last line to serve as `end-of-file-fixer` workaround.
