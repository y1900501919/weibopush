def convert_sentence(str, map):
    str_lst = list(str)
    result = []
    for char in str_lst:
        if char in map:
            result.append(map[char][0])
            continue
        result.append(char)
    return "".join(result)