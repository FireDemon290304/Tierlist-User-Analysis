# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 13:18:47 2025

@author: Faith
"""

from dataclasses import dataclass
from typing import List, Dict
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


def load_tierlists(filename: str) -> List[TierList]:
    tier_lists = []
    
    with open(filename, 'r') as f:
        for line in f:
            raw = json.loads(line)
            rows = [TierRow(tier_name=r['tierName'], entries=r['entries']) for r in raw['rows']]
            tierlist = TierList(username=raw['userName'], title=raw['title'], rows=rows)
            tier_lists.append(tierlist)
    return tier_lists



# todo move out later (maybe to class obj)
def build_matrix(tierlists: List[TierList]) -> (np.ndarray, List[str]):
    # Get item ids (dict to rem dupes, and sort it)
    # Loop over all, since some users are pricks and enter new things, or leave out things
    item_ids = sorted({entry for tl in tierlists for row in tl.rows for entry in row.entries})
    
    # Convert tl to vector and build matrix
    matrix = np.array([tl.to_vector(item_ids) for tl in tierlists])
    return matrix, item_ids

def data_frame(matrix, ids, lists):
    df = pd.DataFrame(matrix, columns=ids, index=[tl.username for tl in lists])
    print(df)
    return data_frame




























