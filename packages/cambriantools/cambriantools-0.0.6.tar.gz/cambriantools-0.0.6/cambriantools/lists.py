import copy
import itertools
import random

import numpy as np


RANDOM_STATE = None
SHUFFLE = True


def _check(lst: list):
    assert isinstance(lst, list)
    assert len(lst) > 0


def _check_not_empy(lst: list):
    _check(lst)
    assert len(lst) > 0


def index_list(lst, idxs):
    return list(np.array(lst)[idxs])


def get_shuffled(lst,
                 shuffle=SHUFFLE,
                 random_state=RANDOM_STATE,
                 ):
    new_lst = copy.deepcopy(lst)
    if shuffle:
        random.seed(random_state)
        random.shuffle(new_lst)
    return new_lst


def get_shared_shuffled(*args,
                        shuffle=SHUFFLE,
                        random_state=RANDOM_STATE,
                        ):
    idxs = list(range(0, len(args[0])))
    new_idxs = get_shuffled(idxs,
                            random_state=random_state,
                            shuffle=shuffle,
                            )
    new_args = []
    for lst in args:
        new_args += [copy.deepcopy(index_list(lst, new_idxs))]
    return new_args


def check_same_class(elements):
    return all([type(e) == type(elements[0]) for e in elements])


def get_max_elements(elements):
    assert check_same_class(elements), 'all objects must be of the same class'
    max_elements = []
    max_e = max(elements)
    for e in elements:
        if e >= max_e:
            max_elements += [e]
    return [True if e in max_elements else False for e in elements]


def get_min_elements(elements):
    assert check_same_class(elements), 'all objects must be of the same class'
    min_elements = []
    min_e = min(elements)
    for e in elements:
        if e <= min_e:
            min_elements += [e]
    return [True if e in min_elements else False for e in elements]


def list_product(*args):
    return list(itertools.product(*args))  # just a wrap


def split_list_in_batches(lst, batch_size):
    batches = []
    index = 0
    while index < len(lst):
        batches.append(lst[index: index + batch_size])
        index += batch_size
    return batches


def flat_list(list_of_lists):
    return sum(list_of_lists, [])


def get_random_item(lst):
    _check_not_empy(lst)
    idx = 0 if len(lst) == 1 else random.randint(0, len(lst) - 1)
    return lst[idx]


def get_bootstrap(lst: list, n,
                  random_state=RANDOM_STATE,
                  replace=True,
                  ):
    if replace:
        random.seed(random_state)
        bootstrap = [get_random_item(lst) for _ in range(0, n)]  # faster than numpy.choice
        return bootstrap
    else:
        np.random.seed(random_state)
        bootstrap = np.choice(lst, size=n, replace=False)
        return bootstrap


def merge_lists(*args):
    merged = list(itertools.chain(*args))
    return merged


def delete_from_list(lst: list, elements_to_remove: list):
    removed_elements = []
    new_lst = []
    for e in lst:
        if e in elements_to_remove:
            removed_elements += [e]
        else:
            new_lst += [e]
    return new_lst, removed_elements


def all_elements_are_equal(lst: list):
    return lst.count(lst[0]) == len(lst)


def get_lists_intersection(lst1, lst2):
    intersection = list(set(lst1).intersection(set(lst2)))
    return intersection


def check_lists_are_different(lst1, lst2):
    for x in lst1:
        if x in lst2:
            return False
    return True


def check_lists_are_equal(lst1, lst2,
                          checks_len=True,
                          ):
    c = set(lst1) == set(lst2)
    if checks_len:
        c = c and len(lst1) == len(lst2)
    return c
