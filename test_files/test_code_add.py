def add(a, b):
    """
    sums two numbers and returns the result
    """
    return a + b


def return_all_even(lst):
    """
    numbers that are not really odd
    """
    if not lst:
        return None
    return [a for a in lst if a % 2 == 0]
