Configure continuous deployment
===============================

#. Deploy Core to the target machine as described in `DEPLOY.rst <DEPLOY.rst>`__
#. Create deploy ssh key on target machine::

    # Use empty pass phrase
    ssh-keygen -f ~/.ssh/github
    cat ~/.ssh/github.pub >> ~/.ssh/authorized_keys

#. Create github repository secrets::

    CONTINUOUS_DEPLOYMENT_ENABLED=True
    DEPLOY_SSH_KEY=<content of ~/.ssh/github>
    DEPLOY_SSH_HOST=<IP-address or domain name of the target machine>
    DEPLOY_SSH_USER=<username that has the corresponding public key in ~/authorized_keys>

This is a technical last line to serve as `end-of-file-fixer` workaround.
