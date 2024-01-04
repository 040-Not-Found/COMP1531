from circle import Circle
import pytest
def test_small():
	c = Circle(3)
	assert(round(c.circumference, 1)) == 18.8
	assert(round(c.area, 1)) == 28.3
