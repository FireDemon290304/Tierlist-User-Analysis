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
    print("starting node")
    node_server = subprocess.Popen(['node', 'js/server.js'])
    
    #time.sleep(3)
    print("done sleeping")
    return node_server

def main():    
    local = "http://localhost:3000"
    base = "https://tiermaker.com"
    
    url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'
    #url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"
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
        "verbose": False
    }

    print("Getting individual entries...")
    requests.post(local + '/scrape', json=data2)
    
    print("stopping server")
    res1 = requests.post(local + '/stop')
    
    print(res1.content)
    
    # todo handle error responses

if __name__ == "__main__":
    node_proc  = start_server()
    
    main()
    
    time.sleep(1)       # todo race
    
    print('terminating')
    node_proc.terminate()
    node_proc.wait()
    
    """
    try:
        main()
    finally:
        node_proc.terminate()
        node_proc .wait()
    """
        
        
