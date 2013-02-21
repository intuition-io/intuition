import redis

#r = redis.StrictRedis(host='localhost', port=6379, db=0)
r_client = redis.Redis(host='localhost', port=6379, db=0)

r_pubsub = r_client.pubsub()

r_pubsub.subscribe('hello')
for msg in r_pubsub.listen():
    print('Received: ' + msg)

r_client.publish("hello", "world, my friend %s" % ('xavier'))
