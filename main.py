# -*- coding: utf-8 -*-#
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from parser import TierListDataset
from py_fetch import fetch
from typing import Set

outFileMain = "D:/Python Scripts/Tierlist User Analysis/data/fetchResultMain2.json"
outFileSub = "D:/Python Scripts/Tierlist User Analysis/data/fetchResultSub2.jsonl"  # JSON-line separated


def find_dupes(path):
    with open(path, 'r') as f:
        seen = set()
        # num1 = Dict()

        for num, line in enumerate(f):
            line_lower = line.lower()
            if line_lower in seen:
                # num1[num] += 1
                print(f"dupe in line: {num}")
            else:
                seen.add(line_lower)

        # for x in num1:
            # print(f"number of dupes for thing: {}")


def print_df():
    dataset = TierListDataset.from_file(outFileSub)
    print(dataset.to_dataframe())


def get_dataset(url):
    fetch(url, outFileMain, outFileSub)


def main():
    # url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'   # Small (44 of 8) (curr: 346)
    # url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"  # Large (186 of 8)
    # get_dataset(url)
    print_df()
    # find_dupes(outFileSub)
    pass


if __name__ == "__main__":
    main()
