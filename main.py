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
import pandas as pd
# from typing import Set


def extract_clean_slug(url):
    match = re.search(r'tiermaker\.com/categories/[^/]+/([^/?#]+)', url)
    if match:
        slug = match.group(1)
        # Remove a trailing hyphen and digits (e.g. -12345) but not things like boss-2
        return re.sub(r'-\d{4,}$', '', slug)
    return None


def url_to_file(url: str, is_sub: bool):
    name = extract_clean_slug(url)
    return os.path.join(os.getcwd(), 'data', name + ('.jsonl' if is_sub else '.json'))


def find_dupes(path):
    with open(path, 'r', encoding='utf-8') as f:
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


def print_df(filepath):
    dataset = TierListDataset.from_file(filepath)
    print("got dataset")
    print(dataset.to_dataframe())


def get_dataset(url):
    name = extract_clean_slug(url)
    fetch(url, os.path.join(os.getcwd(), 'data'), name)


def main():
    # url = 'https://tiermaker.com/categories/aregentina/streamers-de-argentina-273542'
    # url = "https://tiermaker.com/categories/beauty-cosmetics/shades-of-pink-ranked-305470"  # 33 of 8
    # url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'  # 44 of 8
    # url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"  # 186 of 8
    url = "https://tiermaker.com/categories/pokemon/pokemon-gen-1"  # 731 of 8 (stresstest (wo! (got ~6k users)))
    # get_dataset(url)
    # print_df(url_to_file(url, True))
    # find_dupes(outFileSub)

    dataset = TierListDataset.from_file(url_to_file(url, True))

    # print(dataset.to_dataframe())

    # print(pd.DataFrame(dataset.similarity_matrix))

    print(dataset.similarity_matrix)
    # sim1 = dataset.filtered_similarity(filter_fn=TierListDataset.love_hate_filter)

    # dataset.show_heatmap(sim)
    # dataset.show_heatmap(sim1)

#    idx = 23
#    print(dataset.matrix[idx])
#    print(TierListDataset.love_hate_filter(dataset.matrix[idx]))
    pass


if __name__ == "__main__":
    main()
