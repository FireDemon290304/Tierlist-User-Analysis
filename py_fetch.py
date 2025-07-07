# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 09:10:54 2025

@author: Faith
"""

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

def fetch(mainpage_url: str, outFileMain: str, outFileSub: str):
    node_proc = start_server()
    try:
        
        local = "http://localhost:3000"
        base = "https://tiermaker.com"
        
        #url = 'https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862'
        #url = "https://tiermaker.com/categories/hollow-knight/hollow-knight-bosses-51862"
        
        data1 = {
            "url": mainpage_url,                 # now is string
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
        requests.post(local + '/stop')
        # mind race condition
        # todo handle error responses
    finally:
        time.sleep(1) # will do for now (raceing)
        node_proc.terminate()
        node_proc.wait()


"""
User-agent: Googlebot-Image
Disallow: /images/avatars/

User-agent: *
Disallow: /user/
Disallow: *presentationMode=*
Disallow: /live/
Disallow: /includes/
Disallow: /categories/*/*?page
"""
