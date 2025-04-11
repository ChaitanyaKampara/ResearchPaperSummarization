import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Try setting and getting a key
r.set('name', 'Vaahan')
value = r.get('name')

print("Fetched from Redis:", value.decode())
