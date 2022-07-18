import os
import sys
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379')
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()