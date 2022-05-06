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
-----------------------------------------------------

Connect to receive any incoming messages sent to the **ACCOUNT_NUMBER**.
