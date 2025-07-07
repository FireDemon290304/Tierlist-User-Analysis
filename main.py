# -*- coding: utf-8 -*-# 
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from parser import load_tierlists, build_matrix, data_frame
#from py_fetch import fetch
outFileMain = "data/fetchResultMain.json"
outFileSub = "data/fetchResultSub.jsonl" # JSON-line separated


def main():
    tierlists = load_tierlists(outFileSub)
    
    matrix, ids = build_matrix(tierlists)
    
    data_frame(matrix, ids, tierlists)

if __name__ == "__main__":
    main()
