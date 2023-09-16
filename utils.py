import json
import re


def json_load(pth, verbose=False):
    pth = str(pth)
    if verbose:
        print("Loading {}".format(pth))
    with open(pth, 'r') as f:
        data = json.load(f)
        return data


def json_dump(pth, obj, formatting=True, verbose=False):
    pth = str(pth)
    if verbose:
        print(f'Saving {pth}')
    with open(pth, 'w') as f:
        json.dump(obj, f, indent=4 if formatting else None)


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def natural_keys_obj(text):
    return [atoi(c) for c in re.split(r'(\d+)', str(text))]


def group_list(lst, g):
    assert 0 < g <= len(lst)
    nb = len(lst) // g
    return [lst[nb * (x - 1):nb * x] for x in range(1, g)] + [lst[nb * (g - 1):]]
