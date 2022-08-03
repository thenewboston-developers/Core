Setup Docker Hub repositories
=============================

#. Link GitHub account with Docker Hub at Account Settings -> Linked Accounts For Automated Builds
   ( https://hub.docker.com/settings/linked-accounts )

#. Setup Docker Hub "core" repository with automated builds:

    #. Open https://hub.docker.com/
    #. Click "Create Repository" button
    #. Fill in "Create Repository" form (at https://hub.docker.com/repository/create?namespace=thenewboston )

        #. Name: core
        #. Visibility: Public
        #. Build Settings: click at GitHub icon
        #. GitHub repository: thenewboston-developers/Core
        #. [correct by default] Source Type: Branch
        #. [correct by default] Source: master
        #. [correct by default] Docker Tag: latest
        #. [correct by default] Dockerfile location: Dockerfile
        #. [correct by default] Build Caching: Yes

    #. Click "Create & Build"

#. Setup Docker Hub "core-reverse-proxy" repository with automated builds:

    #. Open https://hub.docker.com/
    #. Click "Create Repository" button
    #. Fill in "Create Repository" form (at https://hub.docker.com/repository/create?namespace=thenewboston )

        #. Name: core-reverse-proxy
        #. Visibility: Public
        #. Build Settings: click at GitHub icon
        #. GitHub repository: thenewboston-developers/Core
        #. [correct by default] Source Type: Branch
        #. [correct by default] Source: master
        #. [correct by default] Docker Tag: latest
        #. Dockerfile location: Dockerfile-reverse-proxy
        #. [correct by default] Build Caching: Yes

    #. Click "Create & Build"
