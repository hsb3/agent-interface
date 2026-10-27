"""Checks on the CLI naming vocabulary."""

from collections import Counter

from helpers import read_json

VOCAB = "skills/agent-interface/references/cli-naming.json"


def test_vocabulary_is_consistent():
    data = read_json(VOCAB)
    verbs = set(data["verbs"])
    maps = (data["synonyms"], data["confirm_synonyms"])
    words = [w for m in maps for w in m]
    assert not [w for w, n in Counter(words).items() if n > 1]
    for word in words:
        assert word not in verbs, word
        assert word not in data["root_commands"], word
    for m in maps:
        for word, verb in m.items():
            assert verb in verbs, (word, verb)
