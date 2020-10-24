Trivia game backend using Sanic
===============================

Backend for online trivia game which provide users system, game match making, and gameplay. The server has been developed using [Sanic](https://github.com/huge-success/sanic) and [Redis](https://redis.io/) and implements a unique architecture to handle large amount of online users (see [System Architecture](#system-architecture) section below).

Support: Python3.6+

Example for mobile app that use this backend: [Google Play](https://play.google.com/store/apps/details?id=com.gruchka.brainfight) / [App store](https://apps.apple.com/us/app/id1522442388)

## Quick start
#### Installing
Clone repository:

    $ git clone https://github.com/adamcohenhillel/trivia-game-backend-sanic.git
Install packages:

    pip install -r requirements.txt
    
#### Run

    python main.py

> Make sure you have Redis server up and running, see settings.py to modify redis server address

> For production, please see [Production suggestions](#production-suggestions) section below

#### Endpont
Register new user: /auth/register
Login: /auth/register

    

## System Architecture
![Architecture](/images/architecture.png)

## Production suggestions
> using the following suggestions, this backend was able to scale to more than 10,000 connected users simultaneously

#### ASGI
In the Quick Start section above we run the backend app using the command `python main.py` which using the Sanic's inbuilt webserver - and it's fine but not perfect for production. Instead, we can use an alternative ASGI webserver like: Daphne, **Uvicorn**, and Hypercorn:
######  install

    pip install uvicorn

###### run
    
    uvicorn main:app

> We can use ASGI alone without detecated WSGI because we don't serve static files in put backend

#### Linux machine
asdasdasdasd

#### Redis server
If the Redis server run on the same machine with the backend app, we cam modify
the default settings of the redis server so our backend can go faster and be more durable for a large number of users.
The default method to communicate with the redis server from our backend is by TCP socket, but there is another way - whcich is much better and much more resource efficient - using UNIX sockets.
Open the redis conf file:

    vim /etc/redis/redis.conf

Uncomment the lines:

    unixsocket /var/run/redis.sock
    unixsocketperm 700

Restart redis server:
    
    sudo service redis-server restart`
