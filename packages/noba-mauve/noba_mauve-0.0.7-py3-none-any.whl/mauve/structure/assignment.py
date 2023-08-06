from mauve.constants import ASSIGNMENT_WORDS


# TODO: only extract first assignment, then feed the tail into a parser that
# may analyse again in the tree
def extract_assignments(sentence):
    """
    Given segments, pull out the assignments made in the segments

    Issue around is not where the assignment join doesn't contain the negation.
    Not too worried though

    :param sentence: Sentence object
    :return:
    """

    text = sentence.text

    good = False
    for joining_word in ASSIGNMENT_WORDS:
        if ' ' + joining_word + ' ' in text:
            good = True
            break

    if not good:
        return []

    from mauve.models.sentence import Sentence
    deptree = Sentence(text).deptree

    assignments = []

    # Still interesting things around -ly and wordy things

    for equal_node in deptree.equals:

        # FIXME: Do not bridge over punctuation (and possibly find examples
        # where it's appropriate)

        # expl can usually be second part of an assignment?

        relevant_deps = ['nsubj', 'dobj', 'pobj', 'nsubj', 'expl', 'compound']

        left = deptree.get_closest_before(
            equal_node,
            dep=relevant_deps
        )

        people = sentence.people

        if all([
            not left.segment.is_noun,
            not left.segment.is_prp,
            left.segment.text not in people,
            left.dep not in relevant_deps
        ]):
            continue

        from mauve.models.sentence import Sentence

        assignments.append(
            (
                left,
                equal_node,
                Sentence(
                    ' '.join(
                        [
                            d.text for d in deptree.get_after_node(
                                equal_node,
                                stop_at_punct=True
                            )
                        ]
                    )
                )
            )
        )

    return assignments
