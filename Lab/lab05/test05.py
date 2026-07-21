def group_by(s, fn):
    """Return a dictionary of lists that together contain the elements of s.
    The key for each list is the value that fn returns when called on any of the
    values of that list.

    >>> group_by([12, 23, 14, 45], lambda p: p // 10)
    {1: [12, 14], 2: [23], 4: [45]}
    >>> group_by(range(-3, 4), lambda x: x * x)
    {9: [-3, 3], 4: [-2, 2], 1: [-1, 1], 0: [0]}
    """
    grouped = {}
    for x in s:
        key = fn(x)
        if key in grouped:

            grouped[key].append(x)
        else:
            grouped[key] = [x]
    return grouped

if __name__ == '__main__':
    test_s = [12, 23, 14, 45]
    res = group_by(test_s,lambda p: p // 10)
    print(F"{res}")