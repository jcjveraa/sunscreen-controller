# https://stackoverflow.com/questions/27165607/bool-array-to-integer/27165680#27165680
def binarize_bool_array(array: list[bool]) -> int:
    return sum(v<<i for i, v in enumerate(array[::-1]))
