# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 13:18:47 2025

@author: Faith
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import json
import numpy as np
import pandas as pd
from functools import cached_property


@dataclass
class TierRow:
    """Row = User"""
    tier_name: str
    entries: List[str]


@dataclass
class TierList:
    """Each row is a user. Each column is an item."""
    username: str
    title: str
    rows: List[TierRow]     # This is assumed to be sorted in desc. order based on user ranking

    def __contains__(self, item_id: str) -> bool:
        pass

    def score_map(self) -> Dict[str, int]:
        pass

    def tier_for(self, item_id: str) -> Optional[str]:
        pass

    def items(self) -> Set[str]:
        pass

    def to_vector(self, item_ids: List[str]) -> List[int]:
        """Convert TierList to a vector of normalised scores [0,1] based on tier position"""

        score_map: Dict[str, int] = {}
        num_tiers = len(self.rows)

        if num_tiers < 2:
            # edge: one or empty
            norm = lambda x: 1.0    # Everyone treated as max
        else:
            # i divided by hightest possible score
            norm = lambda i: i / (num_tiers - 1)   # scale [0, 1] because some users add extra tiers

        # make a map to dictate how valuable each row is
        for idx, row in enumerate(reversed(self.rows)):
            score = round(norm(idx), 3)  # index starts at 0, add one because its nicer
            for entry in row.entries:
                score_map[entry] = score

        # Loop through every item in the item_ids (the sorted list of all item entries)
        # get the score attached to that id inside the map
        # Returns a list of length item_ids (one for each possible item in the tierlist)
        return [score_map.get(item_id, -1) for item_id in item_ids]

    # todo
    def similarity(other):
        pass

    def normalize_vector(vector):
        pass


@dataclass
class TierListDataset:
    tierlists: List[TierList]

    # cashe this so that we dont have to calculate the set every time we need it
    # minor oversight
    # added: went from 1,34m runtime for PMG1 to 625ms
    @cached_property
    def all_item_ids(self) -> List[str]:
        # Get item ids (dict to rem dupes, and sort it)
        # Loop over all, since some users are pricks and enter new things, or leave out things
        # from itertools import chain for making this more mem effecient
        return sorted({entry for tl in self.tierlists for row in tl.rows for entry in row.entries}, key=int)

    def usernames(self) -> List[str]:
        return [tl.username for tl in self.tierlists]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.matrix(), columns=self.all_item_ids, index=self.usernames())

    def matrix(self) -> np.ndarray:
        return np.array([tl.to_vector(self.all_item_ids) for tl in self.tierlists])

    @classmethod
    def from_file(cls, filename: str) -> "TierListDataset":
        tier_lists: List[TierList] = []

        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error on line {line_num}: {e}")
                    continue

                if "rows" not in raw:
                    print(f"Missing rows key for line {line_num}:\tSkipping")
                    continue

                rows = [TierRow(tier_name=r['tierName'], entries=r['entries']) for r in raw['rows']]
                tierlist = TierList(username=raw['userName'], title=raw['title'], rows=rows)
                tier_lists.append(tierlist)
        return cls(tierlists=tier_lists)

    # Similarity of two users. Should call u1.similarity(u2) or something.
    # maybe magic methods?
    def cosine_similarity(user1, user2):
        pass

    # Get summary of stats(?)
    def summatr_stats(self):
        pass

    # Save to file
    def to_csv(self):
        pass

    # Remake the tierscores to just be s+, s, a etc.,
    # and fit custom in those bounds to avoid -1 entries
    def normalise_ranks(self):
        pass
