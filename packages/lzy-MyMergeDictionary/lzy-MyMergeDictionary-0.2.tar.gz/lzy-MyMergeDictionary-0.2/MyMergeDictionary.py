def MyMergeDictionary(*args,total=True):
    if total:
        for dict in args[1:]:
            for key, value in dict.items():
                if key in args[0]:
                    args[0][key] += value
                else:
                    args[0][key] = value
    else:
        for K in args[0]:
            if not isinstance(args[0][K], list):
                args[0][K] = [args[0][K]]
        for num, arg in enumerate(args[1:], 2):
            for key, value in arg.items():
                if key in args[0]:
                    args[0][key].append(value)
                else:
                    args[0][key] = [value]
    return args[0]