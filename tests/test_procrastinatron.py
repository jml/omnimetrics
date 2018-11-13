"""Tests for procrastinatron."""

from omnimetrics._procrastinatron import parseYesNo


def test_parse_yes():
    assert parseYesNo("y")
    assert parseYesNo("Y")
    assert parseYesNo("yes")
    assert parseYesNo("YES")
    assert parseYesNo("Yes")
    assert parseYesNo(" Yes ")
    assert parseYesNo("Yessirree ")


def test_parse_empty():
    assert parseYesNo("") is None
    assert parseYesNo("   ") is None
