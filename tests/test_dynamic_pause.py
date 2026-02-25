from collections import deque
from whoare.serve import WhoAreShare, DEFAULT_DYNAMIC_PAUSE_RULES


def make_was(dynamic_pause=True, dynamic_pause_rules=None, pause=41):
    """Create a WhoAreShare instance for testing without needing real URLs."""
    was = WhoAreShare(
        get_domains_url='http://fake/get',
        post_url='http://fake/post',
        token='fake-token',
        torify=False,
        pause_between_calls=pause,
        dynamic_pause=dynamic_pause,
        dynamic_pause_rules=dynamic_pause_rules,
    )
    return was


class TestDefaultDynamicPauseRules:
    """Tests using the default pause rules."""

    def test_high_no_change_rate(self):
        was = make_was()
        was.last_results = deque([1] * 20, maxlen=20)  # 100% no-change
        was.update_dynamic_pause()
        assert was.pause_between_calls == 53

    def test_91_percent(self):
        was = make_was()
        # 19 no-change + 1 change = 95%
        was.last_results = deque([1] * 19 + [0], maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 53

    def test_85_percent(self):
        was = make_was()
        # 17 no-change + 3 change = 85%
        was.last_results = deque([1] * 17 + [0] * 3, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 47

    def test_75_percent(self):
        was = make_was()
        was.last_results = deque([1] * 15 + [0] * 5, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 35

    def test_65_percent(self):
        was = make_was()
        was.last_results = deque([1] * 13 + [0] * 7, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 27

    def test_55_percent(self):
        was = make_was()
        was.last_results = deque([1] * 11 + [0] * 9, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 17

    def test_45_percent(self):
        was = make_was()
        was.last_results = deque([1] * 9 + [0] * 11, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 13

    def test_35_percent(self):
        was = make_was()
        was.last_results = deque([1] * 7 + [0] * 13, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 9

    def test_low_no_change_rate(self):
        was = make_was()
        was.last_results = deque([0] * 20, maxlen=20)  # 0% no-change
        was.update_dynamic_pause()
        assert was.pause_between_calls == 5

    def test_boundary_exactly_90(self):
        was = make_was()
        # exactly 90% -> should NOT match >90, should match >80
        was.last_results = deque([1] * 18 + [0] * 2, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 47

    def test_boundary_exactly_30(self):
        was = make_was()
        # exactly 30% -> should NOT match >30, fallback to last rule
        was.last_results = deque([1] * 6 + [0] * 14, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 5


class TestDynamicPauseDisabled:
    """When dynamic_pause is False, pause should not change."""

    def test_no_change_when_disabled(self):
        was = make_was(dynamic_pause=False, pause=41)
        was.last_results = deque([1] * 20, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 41

    def test_empty_results_no_change(self):
        was = make_was(dynamic_pause=True, pause=41)
        # empty deque
        was.update_dynamic_pause()
        assert was.pause_between_calls == 41


class TestCustomDynamicPauseRules:
    """Tests with user-provided custom rules."""

    def test_custom_two_rules(self):
        rules = [(50, 100), (0, 10)]
        was = make_was(dynamic_pause_rules=rules)
        # 60% no-change -> matches >50
        was.last_results = deque([1] * 12 + [0] * 8, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 100

    def test_custom_fallback(self):
        rules = [(50, 100), (0, 10)]
        was = make_was(dynamic_pause_rules=rules)
        # 25% no-change -> matches >0
        was.last_results = deque([1] * 5 + [0] * 15, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 10

    def test_custom_single_rule(self):
        rules = [(0, 42)]
        was = make_was(dynamic_pause_rules=rules)
        was.last_results = deque([1] * 20, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 42

    def test_custom_rules_not_mutated(self):
        rules = [(80, 60), (50, 30), (0, 5)]
        was = make_was(dynamic_pause_rules=rules)
        was.last_results = deque([1] * 14 + [0] * 6, maxlen=20)
        was.update_dynamic_pause()
        assert was.pause_between_calls == 30
        # rules list should be unchanged
        assert rules == [(80, 60), (50, 30), (0, 5)]


class TestDefaultRulesConstant:
    """Verify DEFAULT_DYNAMIC_PAUSE_RULES is used when none provided."""

    def test_defaults_applied(self):
        was = make_was(dynamic_pause_rules=None)
        assert was.dynamic_pause_rules == DEFAULT_DYNAMIC_PAUSE_RULES

    def test_explicit_rules_override_defaults(self):
        custom = [(70, 99), (0, 1)]
        was = make_was(dynamic_pause_rules=custom)
        assert was.dynamic_pause_rules == custom
        assert was.dynamic_pause_rules is not DEFAULT_DYNAMIC_PAUSE_RULES
