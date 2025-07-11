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
# import pandas as pd
# from typing import Set

urls = [
    'https://tiermaker.com/categories/personal/body-kiss-locations-1318580',
    'https://tiermaker.com/categories/aregentina/streamers-de-argentina-273542',
    'https://tiermaker.com/categories/personal/kelseys-very-specific-fic-tier-list-2-570797',  # AO3 tags
    "https://tiermaker.com/categories/beauty-cosmetics/shades-of-pink-ranked-305470",  # 33
    'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862',  # 44
    "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862",  # 186
    'https://tiermaker.com/categories/pokemon/updated-pokemon-starter-tierlist-1262555',  # 340
    "https://tiermaker.com/categories/pokemon/pokemon-gen-1"  # 731
]


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


def get_dataset(url):
    name = extract_clean_slug(url)
    fetch(url, os.path.join(os.getcwd(), 'data'), name)


def main():
    url = urls[2]

    get_dataset(url)

#    dataset = TierListDataset.from_file(url_to_file(url, True))

    # print(dataset.all_item_ids)

    # dataset.print_user(0)

#    sim = dataset.similarity_matrix
#    sim1 = dataset.filtered_similarity(filter_fn=TierListDataset.top_n_filter)
#    sim2 = dataset.top_n_2(3)

#    print('got sims')

#    dataset.show_heatmap(sim)
#    dataset.show_heatmap(sim1)
#    dataset.show_heatmap(sim2)

    #    idx = 23
    #    print(dataset.matrix[idx])
    #    print(TierListDataset.love_hate_filter(dataset.matrix[idx]))
    pass


if __name__ == "__main__":
    main()
