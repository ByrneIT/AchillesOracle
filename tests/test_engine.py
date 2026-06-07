from achillesoracle.scanner.engine import ScannerEngine


def test_engine_excludes_score_check():
    eng = ScannerEngine('https://example.com')
    modules = [getattr(c, '__module__', '') for c in eng.checks]
    assert not any('security_score_check' in m for m in modules)
