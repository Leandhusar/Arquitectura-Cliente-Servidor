from queue import Queue

q = Queue()
q.put(1)
q.put(2)
q.put(3)

def hola():
    print(q.queue)
    globals()['q'].queue.remove(2)
    print(q.queue)

hola()
print(q.queue)