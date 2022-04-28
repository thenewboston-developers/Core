Project setup
=============

For project setup see OS-dependent installation instructions:

    - `<INSTALL.linux.rst>`_
    - `<INSTALL.macos.rst>`_
    - `<INSTALL.production.rst>`_

Example usage
=============

POST https://thenewboston.network/api/blocks
--------------------------------------------

Request::

    {
      "sender": "eb01f474a637e402b44407f3c1044a0c4b59261515d50be9abd4ee34fcb9075b",
      "recipient": "6fac7f7e2b90173bfc6ef8ee34f9c92438b5eb8f579ef8d84464b820bbfecfc1",
      "amount": 0,
      "payload": {
        "message": "Hey"
      },
      "signature": "df64c0689b2f203c345269aea47d90576c6c37ce168d6084016772f79b2dfb1228de053ec753a2b87e4b404929a8bc6123acf56e7acd178716077e4ddb9b3208"
    }

Response::

    {
      "sender": "eb01f474a637e402b44407f3c1044a0c4b59261515d50be9abd4ee34fcb9075b",
      "recipient": "6fac7f7e2b90173bfc6ef8ee34f9c92438b5eb8f579ef8d84464b820bbfecfc1",
      "amount": 0,
      "payload": {
        "message": "Hey"
      },
      "signature": "df64c0689b2f203c345269aea47d90576c6c37ce168d6084016772f79b2dfb1228de053ec753a2b87e4b404929a8bc6123acf56e7acd178716077e4ddb9b3208"
    }

wss://thenewboston.network/ws/blocks/{ACCOUNT_NUMBER}
-----------------------------------------------------

Connect to receive any incoming messages sent to the **ACCOUNT_NUMBER**.
