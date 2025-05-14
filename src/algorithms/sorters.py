# Merge sort algorithm for sorting objects based on a given key function
def merge_sort(objects, key):
    """
    Merge sort algorithm for sorting objects based on a given key function.
    Args:
    - objects: List of objects to sort.
    - key: A function that extracts the sorting key from each object.
    """
    if len(objects) > 1:
        mid = len(objects) // 2
        left_half = objects[:mid]
        right_half = objects[mid:]

        # Recursively split the lists
        merge_sort(left_half, key)
        merge_sort(right_half, key)

        # Merge process
        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if key(left_half[i]) < key(right_half[j]):
                objects[k] = left_half[i]
                i += 1
            else:
                objects[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            objects[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            objects[k] = right_half[j]
            j += 1
            k += 1

    return objects


# Quick sort algorithm for sorting objects based on a given key function
def quick_sort(arr, key=lambda x: x):
    """
    Quick sort algorithm for sorting objects based on a given key function.
    Args:
    - arr: List of objects to sort.
    - key: A function that extracts the sorting key from each object.
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if key(x) < key(pivot)]
    middle = [x for x in arr if key(x) == key(pivot)]
    right = [x for x in arr if key(x) > key(pivot)]
    return quick_sort(left, key) + middle + quick_sort(right, key)


# Radix sort algorithm for sorting objects based on a string attribute
def radix_sort(objects, get_attribute):
    """
    Radix sort algorithm for sorting objects based on a string attribute.
    Args:
    - objects: List of objects to sort.
    - get_attribute: A function that extracts the attribute to sort by.
    """
    if not objects:
        return objects

    # Find the maximum length string
    max_len = max(len(get_attribute(obj)) for obj in objects)

    # Do counting sort for every character position
    for pos in range(max_len - 1, -1, -1):
        objects = counting_sort(objects, get_attribute, pos)

    return objects


# Counting sort algorithm for sorting objects based on a character position
def counting_sort(objects, get_attribute, position):
    """
    Counting sort algorithm for sorting objects based on a character position.
    Args:
    - objects: List of objects to sort.
    - get_attribute: A function that extracts the attribute to sort by.
    - position: The character position to sort by.
    """
    output = [None] * len(objects)
    count = [0] * 256

    # Store the count of each character
    for obj in objects:
        char = get_attribute(obj)[position] if position < len(get_attribute(obj)) else chr(0)
        count[ord(char)] += 1

    # Change count[i] so that count[i] now contains the actual
    # position of this character in the output array
    for i in range(1, 256):
        count[i] += count[i - 1]

    # Build the output array
    for obj in reversed(objects):
        char = get_attribute(obj)[position] if position < len(get_attribute(obj)) else chr(0)
        output[count[ord(char)] - 1] = obj
        count[ord(char)] -= 1

    return output