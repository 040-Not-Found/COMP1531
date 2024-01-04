'''
Complete the definitions of the following functions using only a single line of code.
'''

def reverse_list(integers):
    '''
    Reverse the list (in-place)
    '''
    integers.reverse()
    print(integers)
    
    return integers
    pass

def minimum(integers):
    '''
    Find and return the lowest number in the list
    '''
    #min_number = [(num) for num in minimum if minimum < num]
    print(min(integers))
    
    return min(integers)
    pass

def sum_list(integers):
    '''
    Return the sum of all numbers
    '''
    print(sum(integers))
    
    return sum(integers)
    pass
