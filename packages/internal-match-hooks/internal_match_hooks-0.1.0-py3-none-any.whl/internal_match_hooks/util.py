import json
import pkg_resources


def load_vocab_refs(vocab_refs_path="resources/variables/vocab_refs.json"):
    with open(pkg_resources.resource_filename(__name__, vocab_refs_path)) as f:
        vocab_refs = json.load(f)
    f.close()
    return vocab_refs