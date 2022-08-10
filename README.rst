Project setup
=============

For project setup see OS-dependent installation instructions:

    - `<INSTALL.linux.rst>`_
    - `<INSTALL.macos.rst>`_
    - `<INSTALL.production.rst>`_

Example usage
=============

POST https://thenewboston.network/api/blocks
++++++++++++++++++++++++++++++++++++++++++++

Request::

    {
      "id": "dc348eac-fc89-4b4e-96de-4a988e0b94e1",
      "amount": 5,
      "payload": {
        "message": "Hey"
      },
      "recipient": "995bd2a4db610062f404510617e83126fa37e2836805975f334108b55523634c",
      "sender": "eb01f474a637e402b44407f3c1044a0c4b59261515d50be9abd4ee34fcb9075b",
      "transaction_fee": 1,
      "signature": "4b86d923cfc7603f39e1d0c36afcec2e454c624b1dc4dd03bf6764e4662162644d0a78c864d16bb7e4608a76db6df0e842a550c52d4811f81d8049f273da8a01"
    }

Response::

    {
      "id": "dc348eac-fc89-4b4e-96de-4a988e0b94e1",
      "sender": "eb01f474a637e402b44407f3c1044a0c4b59261515d50be9abd4ee34fcb9075b",
      "signature": "4b86d923cfc7603f39e1d0c36afcec2e454c624b1dc4dd03bf6764e4662162644d0a78c864d16bb7e4608a76db6df0e842a550c52d4811f81d8049f273da8a01",
      "recipient": "995bd2a4db610062f404510617e83126fa37e2836805975f334108b55523634c",
      "amount": 5,
      "transaction_fee": 1,
      "payload": {
        "message": "Hey"
      }
    }

wss://thenewboston.network/ws/accounts/{ACCOUNT_NUMBER}
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

Connect and authenticate to receive any incoming messages sent to the **ACCOUNT_NUMBER**.

Requests
--------

Authentication::

    {
        "method": "authenticate",
        "token": "6fac7f7e2b90173bfc6ef8ee34f9c92438b5eb8f579ef8d84464b820bbfecfc1$2022-08-11T01:28:47.811436+00:00$14b38d51678062770fd3135fa94925638331160102e7cfb50ab9152ee00a56b03445ea8f36e8d502faf6a3f8413920ddacbd4c763c93108fafff2bb5071ba40f"
    }

token format: {account_number}${iso_formatted_datetime}${signature}

Responses
---------

Authentication success::

    {
        "result": "authenticated"
    }

Authentication failure::

    {
        "result": "unauthenticated"
    }

Create block message::

    {
      "type": "create.block",
      "message": {
        "id": "dc348eac-fc89-4b4e-96de-4a988e0b94e1",
        "sender": "eb01f474a637e402b44407f3c1044a0c4b59261515d50be9abd4ee34fcb9075b",
        "recipient": "6fac7f7e2b90173bfc6ef8ee34f9c92438b5eb8f579ef8d84464b820bbfecfc1",
        "amount": 5,
        "transaction_fee": 1,
        "payload": {
          "message": "Hey"
        },
        "signature": "faddf38480b607861e90b656a367a39e5a09dff00082df3fdbdabcfb71c8677488d68a9b7a9bf963299e00fa8a6480c202b12a01c74bbb349ed929a36c8c860a"
      }
    }

Update account message::

    {
      "type": "update.account",
      "message": {
        "account_number": "6fac7f7e2b90173bfc6ef8ee34f9c92438b5eb8f579ef8d84464b820bbfecfc1",
        "balance": 35
      }
    }
