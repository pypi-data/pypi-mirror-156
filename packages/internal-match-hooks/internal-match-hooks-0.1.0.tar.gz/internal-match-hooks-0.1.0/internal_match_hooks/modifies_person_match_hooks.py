from typing import Iterator, List, Optional, Tuple

from replacy.default_match_hooks import SpacyMatchPredicate
from spacy.tokens import Doc, Span, Token

from internal_match_hooks.util import load_vocab_refs

COPULAR_LEMMATA = ["be", "seem", "look", "appear"]
COPULAR_LINKING_TAGS = ["oprd", "acomp", "attr"]

vocab_refs = load_vocab_refs()


def _one_token_in_span_the_ancestor_of_all_others(s: Span) -> Tuple[bool, Token]:
    """
    :returns a Tuple, begining with a boolean that is
    True if all but one token are a child of the remaining token
    If the first return value is False, the second return value is meaningless
    If the first return value is True, the second return value is the ancestor token
    For example:
    ```python
        doc = nlp("He is a red-neck")
        s = doc[-4:]
        >>> s.text == "a red-neck"
        >>> 4 tokens: a red - neck
    ```
    this function applied to s returns (True, doc[-1]),
    because a, red, and - all are children of neck
    """
    one_is_parent_of_rest = False
    parent_token = s.doc[s.start]
    indices = list(range(s.start, s.end))
    for i in indices:
        rest_i = set(indices) - set([i])
        rest = set(map(lambda i: s.doc[i], rest_i))
        # check all children, but intersect with the span's tokens
        # because the token can have children outside of the span
        if set(s.doc[i].children).intersection(set(s)) == rest:
            one_is_parent_of_rest = True
            parent_token = s.doc[i]

    return one_is_parent_of_rest, parent_token


def _all_tokens_in_span_have_common_ancestor(s: Span) -> Tuple[bool, Token]:
    """
    like a less restrictive _one_token_in_span_the_ancestor_of_all_others
    shared ancestor can be out-of-span
    returns the last token regardless
    """
    return all([list(s[0].ancestors)[0] == list(t.ancestors)[0] for t in s]), s[-1]


def _each_token_in_span_has_next_token_as_ancestor(s: Span) -> Tuple[bool, Token]:
    """
    In doc = nlp("I am a non-white, non-binary, unitarian universalist tech leader.")
    s = doc[3:6]
    non-white
    non has ancestor - has ancestor white
    so we can treat white at "the modifier token"

    If the first return value is False, the second return value is meaningless
    If the first return value is True, the second return value is the token to examine
    """
    condition_met = True
    for i in range(len(s) - 1):
        if list(s[i].ancestors)[0] != s[i + 1]:
            condition_met = False
    return condition_met, s[-1]


def _acceptable(doc: Doc, start: int, end: int) -> Tuple[bool, Token]:
    """
    inputs spacy match tuple (doc, start, end), from which we can find span = doc[start:end]
    "acceptable" here means "can we figure out if this span is acting like a modifier?"
    which I think means "can we figure out if this span has a token that is a modifier,
    and the rest of the span is just kinda syntactic sugar"?
    returns (is_acceptable, index of token to look at)
    """
    if end - start == 1:
        # one token is definitely acceptable, it is the modifier
        return True, doc[start]
    elif end - start == 2 and doc[start].pos_ == "DET":
        # another no-brainer, determiner isn't a modifier, so we can ignore it
        return True, doc[start + 1]
    else:
        # one more situation we can handle (that might be a more general case of "starts with determiner")
        # if all the tokens in the span have the same parent (also in the span), we can assume that parent token
        # is the modifier
        s = doc[start:end]
        (
            span_has_single_parent_in_span,
            span_parent,
        ) = _one_token_in_span_the_ancestor_of_all_others(s)
        if span_has_single_parent_in_span:
            return True, span_parent

        (
            has_subsequent_ancestors,
            final_ancestor,
        ) = _each_token_in_span_has_next_token_as_ancestor(s)
        if has_subsequent_ancestors:
            return True, final_ancestor

        (
            span_has_single_parent,
            span_parent,
        ) = _all_tokens_in_span_have_common_ancestor(s)
        if span_has_single_parent:
            return True, span_parent

        print(
            "match hook modifies_person should only be used "
            "on single token patterns or simple spans"
        )
        return False, doc[start]


def _get_person_token_if_person_string_in_doc(person: str, doc: Doc) -> Optional[Token]:
    person_word_index = [t.i for t in doc if t.text == person]
    if not len(person_word_index):
        return None
    else:
        return doc[person_word_index[0]]


def _matched_token_modifies_person_token(
    matched_token: Token, person_token: Token
) -> bool:
    """
    @HERE - problems with possessives?? FIX THIS!
    TODO - Need to check the chain of possessives:
    if person.token is itself the child, via a `poss` dep, of another noun,
    is that noun a person?
    continue until reach the end of possessives
    if the end is a person, then the matched token modifies the passed in person token
    e.g. the disabled captain's son's friend -- disabled modifies captain (ambiguous but reasonable)
    change to... captain with disabilities's son's friend
    if the end of the possessive chain is not a person, then the matched token modifies that not-person
    e.g. disabled captain's son's center -- disabled "modifies" center, in that this is
    center for captain's son's with disabilities
    """
    return any([c == matched_token for c in person_token.children])


def _is_person(t: Token, person_list: List[str]) -> bool:
    return t.lower_ in person_list or t.ent_type_ == "PERSON"


def _is_noun(t: Token) -> bool:
    return t.pos_ in ["NOUN", "PROPN"]


def _is_subject(t: Token) -> bool:
    return t.dep_ == "nsubj"


def _is_child_of_any_token_in_collection(
    token: Token, collection: Iterator[Token]
) -> bool:
    return any([token in t.children for t in collection])


def _has_person_subject(tokens: Iterator[Token], person_list: List[str]) -> bool:
    return any(
        [_is_person(t, person_list=person_list) and _is_subject(t) for t in tokens]
    )


def _modifies_person_as_attribute(doc, start, end, matched_token, list_items) -> bool:
    # no list_key and/or variable_file_path were given
    # check whether the word is modifying a NOUN or PROPN
    if not list_items:
        nouns = filter(lambda t: t.pos_ in ["NOUN", "PROPN"], doc)
        return _is_child_of_any_token_in_collection(matched_token, nouns)
    # needed variables supplied, check if matched token modifies word from list
    for item in list_items:
        maybe_person_token = _get_person_token_if_person_string_in_doc(item, doc)
        if maybe_person_token is None:
            continue
        else:
            person_token = maybe_person_token
            if _matched_token_modifies_person_token(matched_token, person_token):
                return True
            else:
                continue
    return False


def _modifies_person_as_complement(
    doc, start, end, matched_token, linking_tags, copular_lemmata, list_items
) -> bool:
    # check if matched token has appropriate dep tag
    if not matched_token.dep_ in linking_tags:
        return False
    # check that it points to a copular verb
    if not matched_token.head.lemma_ in copular_lemmata:
        return False
    if list_items:
        # check that the copular verb's subject is on the long_person list
        return _has_person_subject(matched_token.head.children, list_items)
    else:
        # On this branch we don't care if a person is the subject, so all conditions are already met
        return True


def modifies_person(
    list_key="noun-is-person",
    include_copular_complements=True,
    copular_lemmata=COPULAR_LEMMATA,
    linking_tags=COPULAR_LINKING_TAGS,
    additional_nouns_for_complements=["you", "he", "she", "her", "him", "they", "them"],
    vocab_ref=None,
) -> SpacyMatchPredicate:
    """
    A combination of `modifies_person_adjectively` and `modifies_person_copularly`
    Since match_hooks only AND not OR when you have multiple

    If list_key is None, not specific to persons, e.g any noun works

    This hook is for running against adjectives to see if they are modifying a person,
    such as `the crippled man` or `an exotic woman`.
    if `include_copular_complements` is True (the default), it will look for modifiers across copula-like verbs
    such as `he is black` or `she seems exotic`.
    See examples here https://bit.ly/3eF1NF4
    """
    if list_key:
        persons = vocab_ref[list_key] if vocab_ref is not None else vocab_refs[list_key]
        long_persons = persons + additional_nouns_for_complements
    else:
        persons = None
        long_persons = None

    def _modifies_person(doc: Doc, start: int, end: int) -> bool:
        is_acceptable, matched_token = _acceptable(doc, start, end)
        if not is_acceptable:
            return False

        if include_copular_complements:
            return _modifies_person_as_complement(
                doc,
                start,
                end,
                matched_token,
                linking_tags,
                copular_lemmata,
                long_persons,
            ) or _modifies_person_as_attribute(doc, start, end, matched_token, persons)
        else:
            return _modifies_person_as_attribute(
                doc, start, end, matched_token, persons
            )

    return _modifies_person


def modifies_person_adjectively(
    list_key="noun-is-person", vocab_ref=None
) -> SpacyMatchPredicate:
    """
    This hook is for running against adjectives to see if they are modifying an item from a list,
    such as `the crippled man` or `an exotic woman`.
    NOT ones like `he is black` or `she seems exotic`

    If no list_key and/or variable_file_path are given, it checks
    whether the word is modifying a NOUN or PROPN
    """
    if list_key:
        list_items = (
            vocab_ref[list_key] if vocab_ref is not None else vocab_refs[list_key]
        )
    else:
        list_items = None

    def _modifies_person_adjectively(doc: Doc, start: int, end: int) -> bool:
        is_acceptable, matched_token = _acceptable(doc, start, end)
        if not is_acceptable:
            print("unacceptable match")
            return False
        else:
            return _modifies_person_as_attribute(
                doc, start, end, matched_token, list_items
            )

    return _modifies_person_adjectively


def modifies_person_copularly(
    list_key="noun-is-person",
    copular_lemmata=COPULAR_LEMMATA,
    linking_tags=COPULAR_LINKING_TAGS,
    additional_nouns_for_complements=["you", "he", "she", "her", "him", "they", "them"],
    vocab_ref=None,
) -> SpacyMatchPredicate:
    """
    This hook is for running against adjectives to see if they are modifying a person.
    It will look for modifiers across copula-like verbs such as `he is black` or `she seems exotic`.
    NOT `the crippled man` or `an exotic woman`
    See examples here https://bit.ly/3eF1NF4
    """
    persons = vocab_ref[list_key] if vocab_ref is not None else vocab_refs[list_key]
    long_persons = persons + additional_nouns_for_complements

    def _modifies_person_copularly(doc: Doc, start: int, end: int) -> bool:
        is_acceptable, matched_token = _acceptable(doc, start, end)
        if not is_acceptable:
            return False
        return _modifies_person_as_complement(
            doc, start, end, matched_token, linking_tags, copular_lemmata, long_persons
        )

    return _modifies_person_copularly


def possessive_of_list_item(list_key, vocab_ref=None) -> SpacyMatchPredicate:
    """
    This hook is for running against adjectives to see if they are modifying an item from a list,
    such as `the crippled man` or `an exotic woman`.
    NOT ones like `he is black` or `she seems exotic`

    If no list_key and/or variable_file_path are given, it checks
    whether the word is modifying a NOUN or PROPN
    """
    list_items = vocab_ref[list_key] if vocab_ref is not None else vocab_refs[list_key]

    def _possessive_of_list_item(doc: Doc, start: int, end: int) -> bool:
        is_acceptable = end - start == 1
        if not is_acceptable:
            return False
        else:
            matched_token = doc[start]
            candidates = [
                t for t in doc if (t.text in list_items) or (t.lower_ in list_items)
            ]
            possessive_relationships = [
                is_possessive_child_of(matched_token, t) for t in candidates
            ]
            return any(possessive_relationships)

    return _possessive_of_list_item


def is_possessive_child_of(
    matched_token: Token, possible_possessive_parent: Token
) -> bool:
    """
    doc = nlp("The captain's children's shelter is closed")
    captain = doc[1]
    shelter = doc[5]
    is_possessive_child_of(shelter, captain)
    >>> True
    """

    def _token_has_possessive_child(t: Token) -> Tuple[bool, Token]:
        for tok, match in [(tok, tok.dep_ == "poss") for tok in t.children]:
            if match == True:
                return True, tok
        return False, t

    has_poss, t = _token_has_possessive_child(matched_token)
    if possible_possessive_parent == t:
        return True
    else:
        while has_poss:
            next_has_pos, next_t = _token_has_possessive_child(t)
            if possible_possessive_parent == t:
                return True
            if next_has_pos:
                has_poss = True
                t = next_t
            else:
                has_poss = False
    return False


# todo this should not be part of this match hooks, should be in default match hooks
# replacy = "^2.1.1" doesn't have it, while version3.x has it
# we can remove this after we drop support for spacy 2
def end_with(phrase) -> SpacyMatchPredicate:
    def _end_with(doc, start, end):
        return doc[end:].text.lower().strip().endswith(phrase.lower())

    return _end_with