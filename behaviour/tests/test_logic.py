import pytest
from behaviour.src.logic import generate_random_colour

def test_generate_random_colour_returns_valid_colour():
    colour = generate_random_colour()
    assert isinstance(colour, str)
    assert colour.startswith('#')
    assert len(colour) == 7
    # Optionally, check if it's a valid hex colour
    int(colour[1:], 16)
