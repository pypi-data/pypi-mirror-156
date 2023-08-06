import os
import re
import random
import pickle
import logging
from functools import lru_cache
from itertools import chain
from typing import (
    Iterator,
    Any,
    Iterable,
    Mapping
)

import textacy.ke
import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
import fast_json
from compress_pickle import (
    dump,
    load
)

from mauve import (
    ENCORE,
    ENCORE_LG
)
from mauve.models.books.tag import (
    Tag,
    Tags
)
from mauve.constants import (
    GOODREADS_METADATA_PATH,
    TEXT_PATH,
    SPEECH_QUOTES,
)

from mauve.constants.vader import IMPORTANT_WORDS

STEMMER = PorterStemmer()
LEM = WordNetLemmatizer()

logger = logging.getLogger('mauve')

ALPHA_NUM = re.compile('[^a-zA-Z\s\.]+')


def clean_filename(fn: str) -> str:

    replacements = {
        ':': ' - ',
        '?': '',
        '*': '_',
        '"': '',
        '\\': '',
        '<': '',
        '>': ''
    }

    for k, v in replacements.items():
        fn = fn.replace(k, v)
    return fn


def loose_exists(filepath: str) -> bool:
    """

    :param filepath: filepath to get a related file of
    :return: Bool if a file or related file exists
    """
    loose_exists = get_loose_filepath(filepath) is not None
    if not loose_exists:
        logger.warning('Could not get loose filepath for \'%s\'', filepath)
    return loose_exists


def get_loose_filepath(filepath: str) -> str:
    """

    :param: filepath to get a related file of
    :return: The path to the file or loose file that was found
    """
    if os.path.exists(filepath):
        return filepath

    ext = os.path.splitext(filepath)[1]
    if ext == '.bz':
        unextend = os.path.splitext(filepath)[0]
        if os.path.exists(unextend):
            return unextend
    elif ext == '.pickle':
        if os.path.exists(filepath + '.bz'):
            return filepath + '.bz'
        elif os.path.exists(filepath):
            return filepath
    elif ext == '.txt':
        if os.path.exists(filepath + '.bz'):
            return filepath + '.bz'
        if os.path.exists(filepath + '.pickle'):
            return filepath + '.pickle'

    return None


def compress_file(filepath: str) -> Any:
    """
    Compress a file if possible. When reading files that may have been
    compressed use the get_file_content

    :param filepath: Filepath to compress
    """
    ext = os.path.splitext(filepath)[1]
    if ext == '.txt':
        # We want to do this? txt files necessary at all?
        raise NotImplementedError()
    elif ext == '.pickle':
        return dump(
            get_file_content(filepath),
            filepath,
            compression='bz2'
        )
    elif ext == 'bz2':
        pass
    else:
        raise NotImplementedError()


def get_file_content(filepath: str) -> Any:
    """
    Read a file regardless of the extension

    For instance if there's some pickle files and some pickle.bz files
    this will give back the same data as if they were not compressed

    :param filepath: Filepath to read from
    :return: Depending on the ext it may be a pickled obj / str
    """
    filepath = get_loose_filepath(filepath)
    ext = os.path.splitext(filepath)[1]
    if ext == '.txt':
        return open(filepath, 'r').read()
    elif ext == '.pickle':
        return pickle.load(open(filepath, 'rb'))
    elif ext == '.bz':
        return load(os.path.splitext(filepath)[0], 'bz2')
    else:
        raise NotImplementedError()


def get_metadata(source='goodreads') -> Iterable[Mapping[str, str]]:
    """

    :kwarg source: The type of source to get metadata from
    :return: All metadata related to whatever books you're looking for
    :rtype: list
    """
    data = []
    if source == 'goodreads':
        data_dir = GOODREADS_METADATA_PATH

        title_id_map = fast_json.loads(
            open(os.path.join(data_dir, 'title_id_map.json'), 'r').read()
        )

        filenames = os.listdir(data_dir)
        random.shuffle(filenames)

        for filename in filenames:
            if filename == 'title_id_map.json':
                continue
            ext = os.path.splitext(filename)[1]
            if ext != '.json':
                continue
            try:
                tmp = fast_json.loads(
                    open(os.path.join(data_dir, filename), 'r').read()
                )
                real_filename = title_id_map[tmp['book_id']]
                tmp['original_filename'] = real_filename
                data.append(tmp)
            except Exception as ex:
                logger.warning('Problematic file: %s %s' % (filename, ex))
    elif source == 'local_text':
        data_dir = TEXT_PATH

        filenames = os.listdir(data_dir)
        random.shuffle(filenames)

        for filename in filenames:
            data.append(
                {
                    'original_filename': os.path.join(data_dir, filename)
                }
            )
    else:
        raise Exception('No source named %s' % (source))

    return data


def iter_books(source='goodreads') -> Iterator:
    """

    :kwarg source:
    :kwarg: the v of tokens to get from
    :return: generator of book objects
    """
    from mauve.models.books.book import Book
    for book_meta in get_metadata(source=source):
        content_path = os.path.join(
            TEXT_PATH,
            book_meta['original_filename']
        )

        genres = book_meta.get('genres', [])

        tags = Tags()
        for genre in genres:
            tags.append(Tag(name=genre))

        book = Book(
            title=book_meta.get('book_title', None),
            isbn=book_meta.get('isbn', None),
            isbn13=book_meta.get('isbn13', None),
            year_published=book_meta.get('year_first_published', None),
            author=book_meta.get('author', None),
            avg_rating=book_meta.get('average_rating', None),
            tags=tags,
            num_ratings=book_meta.get('num_ratings', None),
            content_path=content_path
        )

        yield book


@lru_cache(maxsize=1000)
def get_en_core_web_sm(text):
    return ENCORE(text)


@lru_cache(maxsize=1000)
def get_en_core_web_lg(text):
    return ENCORE_LG(text)


@lru_cache(maxsize=1000)
def make_spacy_doc(text):
    return textacy.make_spacy_doc(text)


@lru_cache(maxsize=10000)
def get_stem(word) -> str:
    """
    Cachey getting the stem of a word

    Usage:
        >>> get_stem('lovely')
        'love'

    :return: The stem of the word according to nltk
    """
    return STEMMER.stem(word)


@lru_cache(maxsize=10000)
def get_lem(word, pos=None) -> str:
    if not word:
        return word
    if pos is None:
        return LEM.lemmatize(word)
    return LEM.lemmatize(word, pos)


def lower(var: str) -> str:
    """
    Try to get the lower of something. Screw it if
    not, just return the param
    """
    try:
        return var.lower()
    except AttributeError:
        return var


def find_sub_idx(
    original: Iterable[Any],
    repl_list: Iterable[Any],
    start=0,
    end=9999999999999
) -> tuple:
    length = len(repl_list)
    for index in range(start, min(end, len(original))):
        if original[index:index + length] == repl_list:
            return index, index + length


def replace_sub(
    original: Iterable[Any],
    repl_list: Iterable[Any],
    new_list,
    start=0,
    end=999999999999
) -> Iterable[Any]:
    """
    Replace a subset of a list with some other subset

    Usage:
        >>> replace_sub([1,2,3,4], [2,3], [5,6])
        [1,5,6,4]
    """
    length = len(new_list)
    idx = start
    for start, end in iter(lambda: find_sub_idx(original, repl_list, start=idx, end=end), None):
        original[start:end] = new_list
        idx = start + length
    return original


def previous_current_next(iterable: Iterable) -> tuple:
    """
    Make an iterator that yields an (previous, current, next) tuple per element.

    Returns None if the value does not make sense (i.e. previous before
    first and next after last).
    """
    iterable = iter(iterable)
    prv = None
    cur = iterable.__next__()
    try:
        while True:
            nxt = iterable.__next__()
            yield prv, cur, nxt
            prv = cur
            cur = nxt
    except StopIteration:
        yield prv, cur, None


def get_wordnet_pos(tag):
    """
    Map POS tag to first character lemmatize() accepts
    """
    try:
        tag = tag[0].upper()
    except IndexError:
        return None
    else:
        tag_dict = {
            'J': wordnet.ADJ,
            'N': wordnet.NOUN,
            'V': wordnet.VERB,
            'R': wordnet.ADV,
            'S': wordnet.ADJ_SAT
        }
        return tag_dict.get(tag, wordnet.NOUN)


def paragraphs(content: str) -> Iterable[str]:
    """
    Split content into paragraphs. Handy to isolate issues to a
    paragraph rather than let it compound over future paragraphs,

    :param content: string to split into paragraphs
    :return: List split by two newlines
    """
    return content.split('\n')


def sentences(content: str) -> Iterable[str]:
    return [nltk.tokenize.sent_tokenize(para) for para in paragraphs(content)]


def quote_aware_sent_tokenize(content: str) -> Iterable[str]:
    """
    Get sentences but make sure that if they're in one speech part
    that the sentences do not get split away from each other.

    :param content: str content
    :return: list of quote aware sentences
    """
    sentences = []
    for paragraph in paragraphs(content):
        paragraph_sentences = nltk.tokenize.sent_tokenize(paragraph)

        inside_quote = False
        for sentence in paragraph_sentences:
            if inside_quote:
                sentences[-1] += ' ' + sentence
            else:
                sentences.append(sentence)

            if all([
                    str_count_multi(sentence, SPEECH_QUOTES) % 2 != 0,
                    not inside_quote
            ]):
                inside_quote = True
            elif all([
                    str_count_multi(sentence, SPEECH_QUOTES) % 2 != 0,
                    inside_quote
            ]):
                inside_quote = False

    return sentences


def str_count_multi(string: str, things_to_count: Iterable[str]) -> int:
    """

    Usage:
        >>> str_count_multi('one two three two one', ['one', 'three'])
        3

    :return: The occurances of multiple things in a string
    """
    return sum([string.count(thing) for thing in things_to_count])


def rflatten(lst: Iterable[Any]) -> Iterable[Any]:
    '''
    Given a nested list, flatten it.

    Usage:
        >>> rflatten([[[1, 2, 3]], [1, 2]])
        [1, 2, 3, 1, 2]

    :param lst: list to be flattened
    :return: Flattened list
    '''
    if lst == []:
        return lst
    if isinstance(lst[0], list):
        return rflatten(lst[0]) + rflatten(lst[1:])
    return lst[:1] + rflatten(lst[1:])


def flatten(lst: Iterable[Any]) -> Iterable[Any]:
    '''
    Given a nested list, flatten it.

    Usage:
        >>> flatten([[1, 2, 3], [1, 2]])
        [1, 2, 3, 1, 2]

    :param lst: list to be flattened
    :return: Flattened list
    '''
    return list(chain.from_iterable(lst))


def intersperse(lst: Iterable[Any], item: Any) -> Iterable[Any]:
    """

    Usage:
        >>> intersperse([1,2,3], 0)
        [1, 0, 2, 0, 3]
    """
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


def split_include(lst: Iterable[str], splitter: str) -> Iterable[str]:
    """

    Usage:
        >>> split_include(['a b c'], 'a b')
        ['a b', ' c']
    """
    output = []
    for text_part in lst:
        if splitter in text_part:
            output.extend(intersperse(text_part.split(splitter), splitter))
        else:
            output.append(text_part)
    return [o for o in output if o]


def round_down(num: int, divisor: int) -> int:
    return int(num - (num % divisor))


def is_boring_sentimently(content):
    content = ALPHA_NUM.sub('', content)
    content_words = set([i.lower() for i in content.split(' ')])
    intersect = content_words.intersection(IMPORTANT_WORDS)
    return len(intersect) == 0


def extract_only_alphanum(string):
    try:
        return re.sub(r'\W+', '', string)
    except:
        print(string)
