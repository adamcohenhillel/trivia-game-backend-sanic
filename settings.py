WORKERS = 1
ACCESS_LOG = True
PORT = 5000
DEBUG = True
SECRET = "some-secret"
DATABASE = "sqlite://databases/db.sqlite3"
QUESTIONS_FILE = "databases/questions.json"
REDIS_ADDR = "redis://localhost/1"                          # local redis, TCP
#REDIS_ADDR = "redis://:password@redis_url.com:9736/0"      # remote redis, TCP
#REDIS_ADDR = "/var/run/redis/redis-server.sock"            # local redis, UNIX socket