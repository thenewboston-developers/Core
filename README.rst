Core
=============

Core messaging server.

Poetry is a tool for dependency management and packaging in Python. To install, follow the
`installation instructions <https://python-poetry.org/docs/#installation>`_.

Install required packages::

    poetry install

POST http://127.0.0.1:8000/blocks
+++++++++++++

Request::

    {
      "sender": "a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f",
      "recipient": "qd8a4c42ece012b528dda5f469a4706d24459e2eee5a867ff5394cf869466bbe",
      "amount": 5,
      "payload": {
        "message": "Hey"
      }
    }

Response::

    {
      "id": 36,
      "sender": "a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f",
      "recipient": "qd8a4c42ece012b528dda5f469a4706d24459e2eee5a867ff5394cf869466bbe",
      "amount": 5,
      "payload": {
        "message": "Hey"
      }
    }

ws://127.0.0.1:8000/ws/blocks/{ACCOUNT_NUMBER}
+++++++++++++

Connect to receive any incoming messages sent to the **ACCOUNT_NUMBER**.
