import time

def timer(f, name, *args, **kwargs):
    t = time.time()
    r = f(*args, **kwargs)
    print(f"Timer {name} took {time.time() - t} seconds")
    return r