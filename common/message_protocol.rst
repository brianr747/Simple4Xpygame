Message Protocol
================

Introduction
------------

Specify the messages that are supported in the communication protocol.

Must be a single-line string (termination '\n')
Use "|" to separate lists.

First character determines the type of message
'?' = Query  [Normally to server, but can go to Clients.]
'!' = Action
'=' = Response to query, or update.

Note that since we are networked, cannot guarantee anything about the order of responses...

Actions
-------

'!JOIN_PLAYER' Client requests joining as actor in simulation. [Given next available player ID.]

'!DIE!' Server tells a client to %$#& off. Possible triggers: a failed JOIN_PLAYER request,

