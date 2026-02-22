from helpers.direction_helpers import *
import pytest

def test_deg_to_cardinal_pass_none():
    assert deg_to_cardinal(None) == ""

def test_deg_to_cardinal_pass_invalid():
    assert deg_to_cardinal("test") == ""

def test_deg_to_cardinal_pass_90_deg():
    assert deg_to_cardinal("90") == "E"