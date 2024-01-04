def prefix_search(dictionary, key_prefix):
    '''
    Given a dictionary (with strings for keys) and a string, returns a new dictionary containing only the keys (and their corresponding values) for which the string is a prefix. If the string is not a prefix for any key, a KeyError is raised.

    For example,
    >>> prefix_search({"ac": 1, "ba": 2, "ab": 3}, "a")
    {'ac': 1, 'ab': 3}
    '''
    key_dic = {}
    for data in dictionary:
        if key_prefix[0] == data[0]:
            key_dic[data] = dictionary[data]
    
    if key_dic == {}:
        raise KeyError("Key Error")
    else:
        return key_dic
        


#prefix_search({"category": "math", "cat": "animal"}, "b")
'''
if __name__ == '__main__':
    pass
'''

