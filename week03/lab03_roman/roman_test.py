from roman import *
import pytest

def test_roman_five():
    assert roman('V') == 5
    
def test_roman_four():
    assert roman('IV') == 4
    
def test_roman_three():
    assert roman('III') == 3
    
def test_roman_twok():
    assert roman('MM') == 2000
    
def test_roman_fs():
    assert roman('LVI') == 56
    
def test_roman_nt():
    assert roman('XIX') == 19
    
def test_roman_tnn():
    assert roman('MIX') == 1009
    
