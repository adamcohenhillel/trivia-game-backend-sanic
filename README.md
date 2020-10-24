Trivia game backend using Sanic
===============================

Backend for online trivia game which provide users system, game match making, and gameplay. The server has been developed using [Sanic](https://github.com/huge-success/sanic) and [Redis](https://redis.io/) and implements a unique architecture to handle large amount of online users (see [System Architecture](#system-architecture) section below).

Support: Python3.6+

Example for mobile app that use this backend: [Google Play](https://play.google.com/store/apps/details?id=com.gruchka.brainfight) / [App store](https://apps.apple.com/us/app/id1522442388)

## Quick start
#### 1. Installing
Clone repository:

    $ git clone https://github.com/adamcohenhillel/trivia-game-backend-sanic.git
Install packages:

    pip install -r requirements.txt
    
#### 2. Run

    python main.py

> Make sure you have Redis server up and running, see settings.py to modify redis server address
> For production, please see [Production suggestions](#production-suggestions) section below

#### 3. Play
You can run a simple terminal client from `/examples/basic_interact.py`
> To start a game match , you need to run 2 clients!

## System Architecture
![Architecture](/images/architecture.png)

## Production suggestions
> using the following suggestions, this backend was able to scale to more than 10,000 connected users simultaneously

#### 1. ASGI
In the Quick Start section above we run the backend app using the command `python main.py` which using the Sanic's inbuilt webserver - and it's fine but not perfect for production. Instead, we can use an alternative ASGI webserver like **Uvicorn** (also Daphne and Hypercorn):
#####  install

    pip install uvicorn

##### run
    
    uvicorn main:app

> We can use ASGI alone without WSGI because we don't serve static files at all

#### 2. Redis server
> Only if the redis server run on the same machine as the Sanic app!

If the Redis server run on the same machine with the Sanic app, we cam modify the default settings of the redis server so our backend can go faster and be more durable for a large number of users. The default method to communicate with the redis server from our backend is by TCP socket, but there is another way - whcich is much better and much more resource efficient - using UNIX sockets.
Open the redis conf file:

    vim /etc/redis/redis.conf

Uncomment the lines (change unixsocketperm line from 700 to 775):

    unixsocket /var/run/redis.sock
    unixsocketperm 775

Restart redis server:
    
    sudo service redis-server restart

#### 3. Linux machine
There are few changes that you can make to your linux machine to prepare for scale.
Because our app based on sockets connections - which are FILES in Linux OS, there might be a bottleneck here. So - we can increaes the limita for open files in our os (Ubuntu Server 20 LTS):
##### I. open files limitation
run command:

    ulimit -n 1048576
    
##### II. backlog limitation
open the file `/etc/sysctl.conf` and add the following lines:

    net.ipv4.tcp_max_syn_backlog = 1048576
    net.core.somaxconn = 1048576
    net.core.netdev_max_backlog = 1048576

then run the command:

    sysctl --system
