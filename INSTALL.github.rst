Deployment from GitHub registry
===============================

This deployment schema is mostly used for CI purpose, but can be used for manual deployment as well.

#. #. Deploy Core to the target machine as described in `DEPLOY.rst <DEPLOY.rst>`__ except for
   `Install Core <DEPLOY.rst#Install Core>`__ section
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

    DOCKER_REGISTRY_HOST=ghcr.io bash <(wget -qO- https://raw.githubusercontent.com/thenewboston-developers/Core/master/scripts/deploy.sh)

This is a technical last line to serve as `end-of-file-fixer` workaround.
