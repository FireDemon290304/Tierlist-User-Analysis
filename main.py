# -*- coding: utf-8 -*-# 
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from python_js_interface import js_fetch_interface
import json

def main():
    print("Hello World!")
    
    base = "https://tiermaker.com"
    
    #url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'
    url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"
    outFileMain = "data/fetchResultMain.json"
    outFileSub = "data/fetchResultSub.json"
    
    logs = js_fetch_interface(url, outFileMain, isMain = True, verbose = False)
    print(logs)
    
    # Get each entry
    with open(outFileMain, 'r') as file:
        data = json.load(file)
        
    for item in data:
        print(base + item)

    print("Getting individual entries...")
    logs = js_fetch_interface(base + data[3], outFileSub, False, True)
    print(logs)
    
    

if __name__ == "__main__":
    main()
