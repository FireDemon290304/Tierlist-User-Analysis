# -*- coding: utf-8 -*-#
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from parser import TierListDataset
# from py_fetch import fetch
outFileMain = "data/fetchResultMain.json"
outFileSub = "data/fetchResultSub.jsonl"  # JSON-line separated


def main():
    dataset = TierListDataset.from_file(outFileSub)

    print(dataset.to_dataframe())


if __name__ == "__main__":
    main()
