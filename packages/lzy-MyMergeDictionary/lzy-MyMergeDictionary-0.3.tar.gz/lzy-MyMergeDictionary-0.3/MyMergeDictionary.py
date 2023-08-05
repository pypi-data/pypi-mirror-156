def MyMergeDictionary(*args,**kwargs):
    a = set([i for j in args for i in j])
    if kwargs.get('sum'):
        return [[b]+[sum([c[b] for c in args  if b in c])] for b in a]
    elif kwargs.get('total'):
        return [[b]+[c[b] if b in c else None for c in args] for b in a]
    else:
        return [[b]+[c[b] for c in args  if b in c] for b in a]
