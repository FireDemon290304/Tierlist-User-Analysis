# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 13:18:47 2025

@author: Faith
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Callable, Tuple, Type
from pathlib import Path
import json
import numpy as np
import pandas as pd
from functools import cached_property
import matplotlib.pyplot as plt
import seaborn as sns
from numba import njit  # , jit


# using njit because we have checks which cannot be easily vecotrized by numpy
@njit
def has_nan(vec: np.ndarray) -> bool:
    for x in vec:
        if np.isnan(x):
            return True
    return False
    # jit cannot understand this, so make it explicit
    # return np.isnan(vec).any()


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

    def to_vector(self, item_ids: List[str]) -> np.array:
        """Convert TierList to a vector of normalised scores [0,1] based on tier position"""

        score_map: Dict[str, int] = {}
        num_tiers = len(self.rows)

        if num_tiers < 2:
            # edge: one or empty
            # norm = lambda x: 1.0    # Everyone treated as max
            values = [1.0]
        else:
            # i divided by hightest possible score
            # norm = lambda i: i / (num_tiers - 1)   # scale [0, 1] because some users add extra tiers
            # todo check coeefecient (4 as of now) to see what works best
            # result is range from -(co/2) to +(co/2)
            co: int = 3
            # norm = lambda i: (co / 2) - co * (i / (num_tiers - 1))      # Mult 4 to make diff more apparent
            # norm = lambda i: 2 * (i / (num_tiers - 1)) - 1  # flip if wrong
            values = np.linspace(co, -co, num=num_tiers)

        # make a map to dictate how valuable each row is
        for idx, row in enumerate(self.rows):
            score = values[idx]
            for entry in row.entries:
                score_map[entry] = score

        # Loop through every item in the item_ids (the sorted list of all item entries)
        # get the score attached to that id inside the map
        # Returns a list of length item_ids (one for each possible item in the tierlist)
        return np.array([score_map.get(item_id, np.nan) for item_id in item_ids], dtype=float)


@dataclass
class TierListDataset:
    tierlists: List[TierList]
    datasetName: str

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

    # todo stop ignoring nans. infer elsewhere
    # todo figure out how to do this with jit to make it faster because of checks
    @cached_property
    def matrix(self) -> np.ndarray:
        # this is a list of lists, so np.array makes it a 2darray (type ndarray) on its own
        arr = [
            vec
            for tl in self.tierlists
            if (vec := tl.to_vector(self.all_item_ids)) is not None  # and not has_nan(vec)
        ]

        arr = np.array(arr)

        # get the mean value associated with each item
        item_means = np.nanmean(arr, axis=0)

        # replace nans
        nans = np.isnan(arr)
        arr[nans] = np.take(item_means, np.where(nans)[1])

        return arr

    # todo dix nans
    # Similarity of two users
    def cosine_similarity(
        self,
        user1: int | np.ndarray,
        user2: int | np.ndarray,
        filter_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> float:
        """
        Cosine similarity of two users.
        If filter_fn is provided, it will be applied to the shared ratings before computing similarity.

        Returns a value in [-1, 1], where:
          1   = similair ,
          0   = orthogonal (no relation),
         -1   = opposed
        """

        u1, u2 = (self.matrix[v] if not isinstance(v, np.ndarray) else v for v in (user1, user2))

        # Currently this is irrelevant, because matrix calls filters out nans
        # Want to keep this irrelevant by inferring values later on
        mask = (u1 != np.nan) & (u2 != np.nan)

        # Only compare positions where both users have data
        if not np.any(mask):
            return 0.0

        u1m, u2m = u1 * mask, u2 * mask

        if filter_fn:
            u1m, u2m = filter_fn(u1m), filter_fn(u2m)

        norms = np.linalg.norm([u1m, u2m], axis=1)
        if norms[0] == 0 or norms[1] == 0:
            return 0.0

        return np.dot(u1m, u2m) / (norms[0] * norms[1])

    # todo deal with nan better
    @staticmethod
    @njit
    def fast_cosine(u1, u2):
        dot, norm1, norm2 = 0.0, 0.0, 0.0
        for i in range(len(u1)):
            if u1[i] != np.nan and u2[i] != np.nan:
                dot += u1[i] * u2[i]
                norm1 += u1[i] ** 2
                norm2 += u2[i] ** 2
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot / (norm1**0.5 * norm2**0.5)

    @cached_property
    def similarity_matrix(self) -> np.ndarray:
        # Get norms for each row (row=(axis=1))
        # Find the norm for each vector in the filtered matrix
        # The args for np, says to take it for the vectors, not the matrix
        norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)

        # here, we devide each individual vector with its corresponding norm,
        # and storing a new version of the vector, but now its magnitude is 1
        normalised = self.matrix / (norms + 1e-10)  # Add small to avoid undefined

        # Here we calculate the cosine similarity
        # Because all vectors are mag 1,
        # the calc simplifies to u dot v for each entry m[u][v] and m.T[u][v]
        # when calculating this, we transpose norm because then we can mult,
        # org row by evert other row (org Transpose org.T)
        return normalised @ normalised.T

    def filtered_similarity(self, filter_fn: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
        n = len(self.matrix)
        sim = np.zeros((n, n), dtype=float)

        # todo filter vec i before, so no dup calcs
        for i in range(n):
            v_i = filter_fn(self.matrix[i])
            for j in range(i, n):
                v_j = filter_fn(self.matrix[j])
                # s = self.cosine_similarity(i, j, filter_fn)
                s = self.cosine_similarity(v_i, v_j, filter_fn)
                sim[i, j], sim[j, i] = s, s
        return sim

    def sim_test(self) -> np.ndarray:
        # Filter
        filtered = self.matrix[:, [0, -1]]
        norms = np.linalg.norm(filtered, axis=1, keepdims=True)
        normalised = filtered / (norms + 1e-10)
        return normalised @ normalised.T

    def top_n_2(self, n: int = 3) -> np.ndarray:
        filtered = self.matrix[:, :n]
        norms = np.linalg.norm(filtered, axis=1, keepdims=True)
        normalised = filtered / (norms + 1e-10)
        return normalised @ normalised.T

    def love_hate_2(self, n: int = 1) -> np.ndarray:
        """Get first and last. Love-Hate but better"""
        n = min(n, self.matrix.shape[1] // 2)
        filtered = self.matrix[:, [*range(n)] + [*range(-n, 0)]]
        norms = np.linalg.norm(filtered, axis=1, keepdims=True)
        normalised = filtered / (norms + 1e-10)
        return normalised @ normalised.T

    @staticmethod
    def love_hate_filter(vector: np.ndarray) -> np.ndarray:
        result = np.zeros_like(vector)
        result[0] = vector[0]
        result[-1] = vector[-1]
        return result

    @staticmethod
    def top_n_filter(vector: np.array, n: int = 3) -> np.array:
        """Only keep items that are in the top n for that user"""
        mask = np.zeros_like(vector)
        mask[:n] = 1
        return vector * mask

    @staticmethod
    def non_neutral_filter(vector: np.array, neutral: Tuple[float, float] = (-0.5, 0.5)) -> np.array:
        mask = (vector < neutral[0]) | (vector > neutral[1])
        return vector * mask

    @staticmethod
    def z_extremes_filter(vector: np.array, z_threshold: float = 1.0) -> np.array:
        """Only keep items that are extreme for that user. This detects personal outliers."""
        mean = np.mean(vector)
        std = np.std(vector)
        z_scores = (vector - mean) / (std + 1e-9)
        mask = np.abs(z_scores) > z_threshold
        return vector * mask

    @staticmethod
    def demean_filter(vector: np.array) -> np.array:
        mask = vector != 0
        mean = np.sum(vector) / (np.count_nonzero(mask) + 1e-10)
        return (vector - mean) * mask

    # Get summary of stats(?)
    def summaty_stats(self):
        """Calculate the rank and nullspace of the matrix, along with som other info (todo)."""
        pass

    def show_heatmap(self, data, bound: int = 1) -> None:
        plt.figure(figsize=(10, 8))
        sns.clustermap(data, cmap='coolwarm', center=0, vmax=bound, vmin=-bound)
        plt.title(f"Usersimilarity Heatmap for '{self.datasetName.upper()}'")
        plt.xlabel('user')
        plt.ylabel('user')
        plt.show()

    @classmethod
    def from_file(cls: Type['TierListDataset'], filepath: str) -> "TierListDataset":
        tier_lists: List[TierList] = []
        dataset_name = Path(filepath).stem

        with open(filepath, 'r', encoding='utf-8') as f:
            seen = set()
            num_exact_copies = 0
            num_missing_key = 0
            num_no_data = 0
            num_correct = 0

            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error on line {line_num}:\t\t{e}")
                    continue

                if "rows" not in raw:
                    print(f"Missing rows key for line {line_num}")
                    num_missing_key += 1
                    continue

                rows = [TierRow(tier_name=r['tierName'], entries=r['entries']) for r in raw['rows']]
                tierlist = TierList(username=raw['userName'], title=raw['title'], rows=rows)

                if line not in seen:
                    # Skip users with less than 3 tier ranks
                    # also skips users who only have one single tier with everything in it
                    num_filled_lists = 0
                    for trow in tierlist.rows:
                        if len(trow.entries) > 1:
                            num_filled_lists += 1

                    # ignore those who put everything inside one or two tiers
                    # and who make empty lists
                    if len(tierlist.rows) < 3 or num_filled_lists < 3:
                        print(f"No data for user '{tierlist.username}' on line {line_num}")
                        num_no_data += 1
                        continue

                    num_correct += 1
                    tier_lists.append(tierlist)
                    seen.add(line)
                else:
                    print(f"Skipping exact string duplicate for user: '{tierlist.username}' on line {line_num}")
                    num_exact_copies += 1
                    # print(f"skip duplicate user: '{tierlist.username}' on line {line_num}")

        total = num_correct + num_exact_copies + num_missing_key + num_no_data
        fraction: float = num_correct / total
        procent = round(fraction * 100, 3)
        print(f"\nFinished parsing entries for {dataset_name.upper()}\n")
        print(f"For the sake of quantifying my frustration:\n\tNumber of currupted entries:\t\t\t\t\t\t\t\t\t\t{num_missing_key}\n\tNumber of users who made malformed lists:\t\t\t\t\t\t\t{num_no_data}\n\tNumber of times a list was submitted multiple times:\t\t\t\t{num_exact_copies}\n\nLeaving the 'grand total' number of accepted entries as:\t\t\t\t{num_correct}\n(Which includes those who submitted lists with missing items...)")
        print(f"This brings the procentage of users who can read up to {procent} %\n\n\n")
        return cls(tierlists=tier_lists, datasetName=dataset_name)

    def print_user(self, n: int):
        print(self.matrix[n])

    # Save to file
    def to_csv(self):
        pass
