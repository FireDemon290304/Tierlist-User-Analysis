# -*- coding: utf-8 -*-#
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from parser import TierListDataset, Algos
from py_fetch import fetch
import os
import re
import numpy as np
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


def extract_clean_slug(url) -> str | None:
    match = re.search(r'tiermaker\.com/categories/[^/]+/([^/?#]+)', url)
    if match:
        slug = match.group(1)
        # Remove a trailing hyphen and digits (e.g. -12345) but not things like boss-2
        return re.sub(r'-\d{4,}$', '', slug)
    return None


def url_to_file(url: str, is_sub: bool) -> str:
    name = extract_clean_slug(url)
    if name is not None:
        return os.path.join(os.getcwd(), 'data', name + ('_sub_data' if is_sub else '_main_links') + '.jsonl')
    return ''


def get_dataset(url):
    name = extract_clean_slug(url)
    if name is not None:
        fetch(url, os.path.join(os.getcwd(), 'data'), name)


def main():
    print()
#    url = urls[5]

#    ua = 0
#    ub = 200

#    get_dataset(url)

#    dataset = TierListDataset.from_file(url_to_file(url, True))
    A = np.array([[0.7, 0.1, 0.1], [0.2, 0.8, 0.2], [0.1, 0.1, 0.7]], dtype=np.double)
    res = Algos.get_eigen(A)
    print(res)
#    for i in range(len(orthNorm)):
#        print(np.linalg.norm(orthNorm[i]))

#    try:
#        print(Algos.gram_schmidt_explicit(dataset.matrix))      # Users not independent: Some users have derivative taste
#        print(Algos.gram_schmidt_explicit(dataset.matrix.T))    # Items are independent: Item-space is full-rank
#    except Exception as e:
#        print(e)


#    print(dataset.all_item_ids)

#    dataset.print_user(0)


#    dataset.plot_contrast(ua, ub)

#    print('got sims')


    pass


if __name__ == "__main__":
    main()
