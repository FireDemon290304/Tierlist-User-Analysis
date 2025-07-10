# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 13:18:47 2025

@author: Faith
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from pathlib import Path
import json
import numpy as np
import pandas as pd
from functools import cached_property
import matplotlib.pyplot as plt
import seaborn as sns


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

    # @cached_property
    def to_vector(self, item_ids: List[str]) -> np.array:
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
        return np.array([score_map.get(item_id, -1) for item_id in item_ids], dtype=float)


@dataclass
class TierListDataset:
    tierlists: List[TierList]
    datasetName: str

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
        return pd.DataFrame(self.matrix, columns=self.all_item_ids, index=self.usernames())

    @cached_property
    def matrix(self) -> np.ndarray:
        return np.array([tl.to_vector(self.all_item_ids) for tl in self.tierlists])

    @classmethod
    def from_file(cls, filepath: str) -> "TierListDataset":
        tier_lists: List[TierList] = []
        dataset_name = Path(filepath).stem

        with open(filepath, 'r', encoding='utf-8') as f:
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
        return cls(tierlists=tier_lists, datasetName=dataset_name)

    # Similarity of two users
    def cosine_similarity(self, user1: int, user2: int) -> float:
        """
        Cosine similarity of two users.
        Returns a value in [-1, 1], where:
          1   = same preferences,
          0   = orthogonal (no relation),
         -1   = totally opposed.
        """

        u1, u2 = self.matrix[user1], self.matrix[user2]

        # Only compare positions where both users have data (not -1)
        mask = (u1 != -1) & (u2 != -1)
        if not np.any(mask):  # no shared ratings: no similarity/undefined
            return 0.0

        u1m, u2m = u1[mask], u2[mask]
        norms = np.linalg.norm([u1m, u2m], axis=1)

        if norms[0] == 0 or norms[1] == 0:
            return 0.0

        return np.dot(u1, u2) / (norms[0] * norms[1])

    # maybe cashe this, its expensive (kind of)
    @cached_property
    def similarity_matrix(self) -> np.ndarray:
        # def dim
        n = len(self.tierlists)
        sim = np.zeros(shape=(n, n), dtype=float)  # make arr of dim n,n. fill zeros

        # build
        for i in range(n):
            for j in range(i, n):  # start i stop n: uppertriangle (avoid double counting)
                s = self.cosine_similarity(i, j)
                sim[i, j], sim[j, i] = s, s
        print('made heatmap')
        return sim

    def show_heatmap(self) -> None:
        plt.figure(figsize=(10, 8))
        sns.heatmap(self.similarity_matrix,
                    cmap='coolwarm',
                    center=0,
                    vmax=1,
                    vmin=-1)
        plt.title(f"Usersimilarity Heatmap for '{self.datasetName}'")
        plt.xlabel('user')
        plt.ylabel('user')
        plt.show()

    # Get summary of stats(?)
    def summaty_stats(self):
        """Calculate the rank and nullspace of the matrix, along with som other info (todo)."""
        pass

    # Save to file
    def to_csv(self):
        pass
