# Circular iterator (Citerate)

Bi-dimensional matrix iterator starting from any point (i, j), iterating layer by layer around the starting coordinates.

## Usage

    pip install citerate

As of __14 july 2021__ it contains one method `citerator`

    from citerate import citerator

## Examples

Using the example data set:

    TEST_SET = [
        [10, 11, 12, 13, 14],
        [25, 2,  3,  4,  15],
        [24, 9,  1,  5,  16],
        [23, 8,  7,  6,  17],
        [22, 21, 20, 19, 18],
    ]

Iterate over the set layer by layer starting from coordinates (i=2, j=2) and print each layer as a list of it's corresponding values.

    for layer in citerate.citerator(TEST_SET, i=2, j=2, layer=True):
        print(layer)

Yields:

    [1]
    [2, 3, 4, 5, 6, 7, 8, 9]
    [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]


Iterate over the set value by value starting from coordinates (i=2, j=2) and print each value individually.

    for value in citerate.citerator(TEST_SET, i=2, j=2):
        print(value, end=' ')

Yields:

    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25

# Footnotes

- It is NOT mandatory to iterate starting from the central coordinates or for the matrix to be uniform.
- It HAS to be bi-dimenstional and follow a "list of lists" pattern.
