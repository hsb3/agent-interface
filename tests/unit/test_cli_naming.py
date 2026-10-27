"""Checks on the CLI naming vocabulary."""

from collections import Counter
import json

from helpers import ROOT

VOCAB = ROOT / "skills/agent-interface/references/cli-naming.json"


def no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    assert len(keys) == len(set(keys)), [k for k, n in Counter(keys).items() if n > 1]
    return dict(pairs)


def test_vocabulary_is_consistent():
    # json.loads keeps only the last of two equal keys, so a repeat inside one map needs the hook.
    data = json.loads(VOCAB.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)
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
