===========================
Core Deployment Guide (AWS)
===========================

Key Pair
++++++++

#. Make sure these are set for ``~/.ssh/config``::

    Host *
    UseKeychain yes

#. Create new keypair via AWS UI::

    # update permissions to be read only
    chmod 400 ~/Downloads/Bucky-iMac.pem

    # add the key to your agent
    ssh-add -K ~/Downloads/Bucky-iMac.pem

Create EC2 instance
+++++++++++++++++++

Create an EC2 instance::

    t2.micro
    Ubuntu 24.04 64-bit (x86), 16Gb storage
    Allow SSH, HTTP, HTTPs

Setup domain
++++++++++++

Domain Name
-----------

#. Navigate to EC2 > Network and Security > Elastic IPs
#. Click the "Allocate Elastic IP address" button
#. Click the Allocate button
#. Give that Elastic IP a more memorable name
#. Select it and choose click on "Associate Elastic IP address"
#. Choose your core instance in "Instance" dropdown box
#. Check "Allow this Elastic IP address to be reassociated"
#. Click on "Associate"
#. Test by SSHing into the instance using the new IP.

Update your domain's DNS records to point to your elastic IP
------------------------------------------------------------

#. Create type A DNS record for your domain, which points to the Elastic IP
#. Test by SSHing into the instance using the domain name

Install Docker
++++++++++++++
To install Docker (known working version 27.0.3, build 7d4bcd8) on target machine follow the instructions below
(based on https://docs.docker.com/engine/install/ubuntu/ ).

Login to the EC2 instance
-------------------------

Login to the EC2 instance::

    ssh ubuntu@DOMAIN_NAME

Uninstall any existing versions of Docker
-----------------------------------------

It's OK if apt reports that none of these packages are installed::

    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

Set up the repository
---------------------

Before you install Docker Engine for the first time on a new host machine,
you need to set up the Docker repository. Afterward, you can install and update Docker from the repository::

    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

Install Docker Engine
---------------------

#. Install Docker Engine::

    # install the latest version of Docker Engine, containerd, and Docker Compose
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # verify that Docker Engine is installed correctly by running the hello-world image
    sudo docker run hello-world

#. Add your user to docker group

   Docker Engine is installed and running. The docker group is created but no users are added to it::

    sudo usermod -aG docker $USER
    exit

    # Login to the EC2 instance again
    ssh ubuntu@DOMAIN_NAME

#. Pull the images::

    docker pull thenewboston/core
    docker pull thenewboston/core-reverse-proxy

Install Core
++++++++++++

Run the deployment script::

    bash <(wget -qO- https://raw.githubusercontent.com/thenewboston-developers/Core/master/scripts/deploy.sh)

Create superuser
++++++++++++++++

Optionally create superuser::

    docker compose exec -it core poetry run python -m core.manage createsuperuser

This is a technical last line to serve as `end-of-file-fixer` workaround.
