

def find(pred, iterable):
    for element in iterable:
        if pred(element):
            return element
    return None
