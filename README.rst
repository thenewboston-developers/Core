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
      "amount": 5,
      "payload": {
        "message": "Hey"
      },
      "recipient": "995bd2a4db610062f404510617e83126fa37e2836805975f334108b55523634c",
      "sender": "73b3c1c2f1cc307969060ab84a0e34937c6442913e4774ec8f3e2b4fe1926cf8",
      "transaction_fee": 1,
      "signature": "d20e3b4ea06e9fe1ac190928e2bd5b27ec6ec1ba2c05eb303da44428b8d6d03684ef0965acdda361d5c2913712c07b52b3c96ff106754e750d64625330bc7d04"
    }

Response::

    {
      "id": 42,
      "sender": "73b3c1c2f1cc307969060ab84a0e34937c6442913e4774ec8f3e2b4fe1926cf8",
      "signature": "d20e3b4ea06e9fe1ac190928e2bd5b27ec6ec1ba2c05eb303da44428b8d6d03684ef0965acdda361d5c2913712c07b52b3c96ff106754e750d64625330bc7d04",
      "recipient": "995bd2a4db610062f404510617e83126fa37e2836805975f334108b55523634c",
      "amount": 5,
      "transaction_fee": 1,
      "payload": {
        "message": "Hey"
      }
    }

wss://thenewboston.network/ws/blocks/{ACCOUNT_NUMBER}
-----------------------------------------------------

Connect to receive any incoming messages sent to the **ACCOUNT_NUMBER**.
