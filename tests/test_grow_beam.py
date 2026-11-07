"""GB 50011 cl. 6.3.1 kept when R13/R14 grow a beam (P1, 7 Nov 2026)."""


def test_grow_beam_keeps_631():
    """Deeper while h/b <= 4 and clear span/h >= 4; otherwise wider (cl. 6.3.1)."""
    from shellbench.generator import grow_beam
    assert grow_beam(300, 600, 7.2, 500) == (300, 650, "deeper")
    assert grow_beam(300, 1200, 7.2, 500) == (350, 1200, "wider")   # 1250/300 > 4
    assert grow_beam(500, 1650, 7.2, 500) == (550, 1650, "wider")   # clear span 6700/1700 < 4
