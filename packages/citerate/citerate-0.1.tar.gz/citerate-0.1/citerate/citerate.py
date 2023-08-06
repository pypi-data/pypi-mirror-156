def citerator(data: list, x: int, y: int, layer = False) -> list:
    """Bi-dimensional matrix iterator starting from any point (i, j),
    iterating layer by layer around the starting coordinates.

    Args:
        data (list): Data set to iterate over.
        x (int): X starting coordinate.
        y (int): Y starting coordinate.

    Optional args:
        layered (bool): Yield value by value or entire layer.

    Yields:
        value: Layer value.
        list: Matrix layer.
    """

    if layer:
        yield [data[x][y]]
    else:
        yield data[x][y]

    for depth in range(len(data)):
        l = []
        # top row
        wpos = x - depth - 1
        for i in range(y - depth - 1, y + depth + 1):
            if (not (i < 0
                or wpos < 0
                or i >= len(data)
                or wpos >= len(data))
                and not (wpos >= len(data)
                or i >= len(data[wpos]))):
                l.append(data[wpos][i])
        # right column
        hpos = y + depth + 1
        for i in range(x - depth - 1, x + depth + 1):
            if (not (i < 0
                or hpos < 0
                or i >= len(data)
                or hpos >= len(data))
                and not (hpos >= len(data)
                or hpos >= len(data[i]))):
                l.append(data[i][hpos])
        # bottom row
        wpos = x + depth + 1
        for i in reversed(range(y - depth, y + depth + 2)):
            if (not (i < 0
                or wpos < 0
                or i >= len(data)
                or wpos >= len(data))
                and not (wpos >= len(data)
                or i >= len(data[wpos]))):
                l.append(data[wpos][i])
        # left column
        hpos = y - depth - 1
        for i in reversed(range(x - depth, x + depth + 2)):
            if (not (i < 0
                or hpos < 0
                or i >= len(data)
                or hpos >= len(data))
                and not (hpos >= len(data)
                or hpos >= len(data[i]))):
                l.append(data[i][hpos])

        if l:
            if layer:
                yield l
            else:
                for v in l:
                    yield v
        else:
            break
