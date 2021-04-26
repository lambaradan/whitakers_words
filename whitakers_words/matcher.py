from typing import Callable, Sequence

from .datatypes import DictEntry, Inflect, Stem
from .enums import Degree


class Matcher:
    def __init__(self, stem: Stem, infl: Inflect):
        self.stem = stem
        self.infl = infl
        self.function: Callable[[Stem, Inflect, DictEntry], bool]
        if infl["pos"] != stem["pos"]:
            if infl["pos"] == "VPAR" and stem["pos"] == "V":
                self.function = _vpar_checker
            else:
                self.function = _dummy_false
        elif stem["pos"] == "N":
            self.function = _noun_checker
        elif stem["pos"] == "ADV":
            self.function = _adv_checker
        elif stem["pos"] == "ADJ":
            self.function = _adj_checker
        elif stem["pos"] == "V":
            self.function = _verb_checker
        else:
            self.function = _basic_matcher

    def check(self, word: DictEntry) -> bool:
        return self.function(self.stem, self.infl, word)


def _dummy_false(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    return False


def _vpar_checker(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    if infl["form"][3] == "PERF":
        return stem["orth"] == word["parts"][-1]
    return stem["orth"] == word["parts"][0]


def _noun_checker(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    if infl["n"] == stem["n"] or (infl["n"][0] == stem["n"][0] and infl["n"][-1] == 0):
        return infl["form"][-1] == stem["form"][0] or infl["form"][-1] == "C"
    return False


def _adj_checker(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    if not _basic_matcher(stem, infl, word):
        return False
    if stem["form"][-1] == "X":
        if stem["orth"] in word["parts"]:
            return get_degree(word["parts"][1:], stem["orth"]) == infl["form"][-1]
    return stem["form"][-1] == infl["form"][-1]


def _adv_checker(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    if stem["form"] == ["X"]:
        if stem["orth"] in word["parts"]:
            return get_degree(word["parts"], stem["orth"]) == infl["form"][-1]
    return stem["form"] == infl["form"]


def _verb_checker(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    if (infl["n"] == stem["n"] or infl["n"][0] == 0 or
            (infl["n"][0] == stem["n"][0] and infl["n"][1] == 0)):
        if infl["form"][0] in ["PERF", "FUTP", "PLUP"]:
            return stem["orth"] == word["parts"][2]
        return stem["orth"] == word["parts"][1]
    return False


def _basic_matcher(stem: Stem, infl: Inflect, word: DictEntry) -> bool:
    if stem["n"]:
        return (infl["n"] == stem["n"] or infl["n"][0] == 0 or
                (infl["n"][0] == stem["n"][0] and infl["n"][1] == 0))
    return True


def get_degree(parts: Sequence[str], stem: str) -> str:
    try:
        return Degree.get_degree_list()[parts.index(stem)]
    except ValueError:
        return Degree.POS.name
