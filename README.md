About
===

Test assignment for Qmoby for Middle Python Developer

This is a battleship type of game. It features reliable message
transmition.

Built with vue2, django, django-channels and redis. Messages are transmitted across
web sockets with guaranteed delivery.

Delivery is guaranteed by:
1. Messages from front end get queued up on the client and only cleared
   after receiving ACK message from server.
2. Messages from the server are put into redis and only cleared
   when ACK message received from the client.
   Servers tries to deliver the messages on client join via django-channels background worker.

Game state is saved in redis too, so if client disconnects he will get the game state on join.

No persistent database is used.

This game doesn't have any authorization methods and relies only
on player name for sending correct state and messages. Should
not be used in production, only for testing purposes.

Deploy
===
1. ```docker build --tag bs:latest .```
3. Make sure that host where are you running docker container has ports 8081, 8000 and 6379 free
2. ```docker run --network=host --name bs1 bs:latest```

To access the game open in browser hostname of docker server with port 8081.
