import pytest
from achillesoracle.scanner.checks.security_score_check import run_check


def test_all_pass_single_check():
    res = run_check('https://example.com',
                    [{'name': 'OK', 'status': 'pass', 'severity': 'low'}])
    assert isinstance(res, dict)
    assert res.get('score') == 100
    assert res.get('grade') == 'A'


def test_critical_error_single_check():
    res = run_check('https://example.com',
                    [{'name': 'CRIT', 'status': 'error', 'severity': 'critical'}])
    assert res.get('score') == 0
    assert res.get('grade') == 'F'


def test_one_warn_among_many_passes():
    checks = [{'name': f'pass{i}', 'status': 'pass', 'severity': 'low'}
              for i in range(49)]
    checks.append({'name': 'warn1', 'status': 'warn', 'severity': 'low'})
    res = run_check('https://example.com', checks)
    # One low-severity warn among many passes should not drop below A-range floor
    assert res.get('score') >= 90


def test_malformed_entries_ignored():
    checks = [None, 'bad', {'name': 'ok', 'status': 'pass'}]
    res = run_check('https://example.com', checks)
    assert 'breakdown' in res
    assert res.get('score') >= 90
