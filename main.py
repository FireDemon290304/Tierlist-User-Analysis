# -*- coding: utf-8 -*-# 
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

# from python_js_interface import js_fetch_interface
import json
import subprocess
import requests
import time

def start_server():
    return subprocess.Popen(['node', 'js/server.js'])

def main():    
    local = "http://localhost:3000"
    base = "https://tiermaker.com"
    
    url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'
    #url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"
    # .. because these are refed inside js folder
    outFileMain = "data/fetchResultMain.json"
    outFileSub = "data/fetchResultSub.jsonl" # JSON-line separated
    
    data1 = {
        "url": url,                 # now is string
        "outFile": outFileMain,
        "isMain": True,
        "verbose": True
    }

    print("getting main")
    requests.post(local + '/scrape', json=data1)
    
    # Get each entry
    with open(outFileMain, 'r') as file:
        data = json.load(file)
        
    for item in data:
        print(item)

    absolute_urls = [f"{base}{path}" for path in data]

    data2 = {
        "url": absolute_urls,                # now is list
        "outFile": outFileSub,
        "isMain": False,
        "verbose": True
    }

    print("Getting individual entries...")
    requests.post(local + '/scrape', json=data2)
    
    print("stopping server")
    requests.post(local + '/stop')
    
    # todo handle error responses

if __name__ == "__main__":
    
    print("starting node")
    node_server = start_server()
    
    time.sleep(3)
    print("done sleeping")
    
    try:
        main()
    finally:
        try:
            node_server.terminate()
        except:
            print('nothing to stop')
        
        
