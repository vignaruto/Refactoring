def flip_and_invert(image):
    return [[1 - p for p in reversed(row)] for row in image]

def count_ones(image):
    return sum(map(sum, image))

def crop(image, top, left, h, w):
    rows = image[top:top + h]
    return [row[left:left + w] for row in rows]

if __name__ == "__main__":
    img = [[1, 0, 0], [1, 0, 1]]
    assert flip_and_invert(img) == [[1, 1, 0], [0, 1, 0]]
    assert count_ones(img) == 3
    assert crop(img, 0, 1, 2, 2) == [[0, 0], [0, 1]]
