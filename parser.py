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


# TODO make this relate to position/index instead, as some lists use different metrics
TIER_SCORES = {
    'S': 5,
    'A': 4,
    'B': 3,
    'C': 2,
    'D': 1
}


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
    rows: List[TierRow]

    def __contains__(self, item_id: str) -> bool:
        pass

    def score_map(self) -> Dict[str, int]:
        pass

    def tier_for(self, item_id: str) -> Optional[str]:
        pass

    def items(self) -> Set[str]:
        pass

    def to_vector(self, item_ids: List[str]) -> List[int]:
        """Convert TierList to a vector"""

        score_map: Dict = {}
        for row in self.rows:
            score = TIER_SCORES.get(row.tier_name.upper(), -1)  # Get value of tier. Default is value -1 (error)
            for entry in row.entries:       # for every entry in a row
                score_map[entry] = score                # set the score in inside the dict for lookup

        # Loop through every item in the item_ids (the sorted list of all item entries)
        # get the score attached to that id inside the map
        # Returns a list of length item_ids (one for each possible item in the tierlist)
        return [score_map.get(item_id, -1) for item_id in item_ids]

    # todo
    def similarity(other):
        pass


@dataclass
class TierListDataset:
    tierlists: List[TierList]

    # todo make more autmatic later
    def all_item_ids(self) -> List[str]:
        # Get item ids (dict to rem dupes, and sort it)
        # Loop over all, since some users are pricks and enter new things, or leave out things
        return sorted({entry for tl in self.tierlists for row in tl.rows for entry in row.entries}, key=int)

    def usernames(self) -> List[str]:
        return [tl.username for tl in self.tierlists]

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.matrix(), columns=self.all_item_ids(), index=self.usernames())

    def matrix(self) -> np.ndarray:
        return np.array([tl.to_vector(self.all_item_ids()) for tl in self.tierlists])

    @classmethod
    def from_file(cls, filename: str) -> "TierListDataset":
        tier_lists: List[TierList] = []

        with open(filename, 'r') as f:
            for line in f:
                raw = json.loads(line)
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
