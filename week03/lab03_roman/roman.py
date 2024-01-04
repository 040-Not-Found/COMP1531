def roman(numerals):
    '''
    Given Roman numerals as a string, return their value as an integer. You may
    assume the Roman numerals are in the "standard" form, i.e. any digits
    involving 4 and 9 will always appear in the subtractive form.

    For example:
    >>> roman("II")
    2
    >>> roman("IV")
    4
    >>> roman("IX")
    9
    >>> roman("XIX")
    19
    >>> roman("XX")
    20
    >>> roman("MDCCLXXVI")
    1776
    >>> roman("MMXIX")
    2019
    '''
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(numerals)):
        if i > 0 and rom_val[numerals[i]] > rom_val[numerals[i - 1]]:
            int_val += rom_val[numerals[i]] - 2 * rom_val[numerals[i - 1]]
        else:
            int_val += rom_val[numerals[i]]
    return int_val
    
    
    
    
    
    
