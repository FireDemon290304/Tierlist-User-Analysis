# -*- coding: utf-8 -*-#
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from parser import TierListDataset
from py_fetch import fetch
import os
import re
# from typing import Set


def extract_clean_slug(url):
    match = re.search(r'tiermaker\.com/categories/[^/]+/([^/?#]+)', url)
    if match:
        slug = match.group(1)
        # Remove a trailing hyphen and digits (e.g. -12345) but not things like boss-2
        return re.sub(r'-\d{4,}$', '', slug)
    return None


def find_dupes(path):
    with open(path, 'r') as f:
        seen = set()
        # num1 = Dict()
        numDupes = 0

        for num, line in enumerate(f):
            line_lower = line.lower()
            if line_lower in seen:
                numDupes += 1
                print(f"dupe in line: {num}")
            else:
                seen.add(line_lower)

        print(f'number of duplicates: {numDupes}')


def print_df(url):
    name = extract_clean_slug(url)
    subFile = os.path.join(os.getcwd(), 'data', name + '.jsonl')
    dataset = TierListDataset.from_file(subFile)
    print("got dataset")
    print(dataset.to_dataframe())


def get_dataset(url):
    name = extract_clean_slug(url)
    fetch(url, os.path.join(os.getcwd(), 'data'), name)


def main():
    # url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'  # 44 of 8
    # url = "https://tiermaker.com/categories/beauty-cosmetics/shades-of-pink-ranked-305470"  # 33 of 8
    # url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"  # 186 of 8
    url = "https://tiermaker.com/categories/pokemon/pokemon-gen-1"  # 731 of 8 (stresstest (wo! (got ~6k users)))
    # url = 'https://tiermaker.com/categories/aregentina/streamers-de-argentina-273542'
    # get_dataset(url)
    print_df(url)
    # find_dupes(outFileSub)
    pass


if __name__ == "__main__":
    main()
