# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 09:10:54 2025

@author: Faith
"""

import json
import subprocess
import requests
import time
import os


def start_server():
    print("spawning child...")
    node_server = subprocess.Popen(['node', 'js/server.js'])
    print('child made')
    return node_server


def fetch(mainpage_url: str, dataDir: str, name: str) -> None:
    node_proc = start_server()
    print('starting fetch')
    try:
        local = "http://localhost:3000"
        base = "https://tiermaker.com"
        fileName = os.path.join(dataDir, name)
        main = fileName + '.json'
        sub = fileName + '.jsonl'

        data1 = {
            "url": mainpage_url,                 # now is string
            "outFile": main,
            "isMain": True,
            "verbose": True
        }

        print("getting main")
        requests.post(local + '/scrape', json=data1)

        # Get each entry
        with open(main, 'r') as file:
            data = json.load(file)

        # for item in data:
        #     print(item)

        absolute_urls = [f"{base}{path}" for path in data]

        print("First few URLs:", absolute_urls[:3])

        # todo fix format here or in js
        data2 = {
            "url": absolute_urls,                # now is list
            "outFile": sub,
            "isMain": False,
            "verbose": False
        }

        print("Getting individual entries...")
        res = requests.post(local + '/scrape', json=data2)

        res.raise_for_status()

        print("...done\nstopping server...")
        requests.post(local + '/stop')
        # mind race condition
        # todo handle error responses
    finally:
        time.sleep(1)  # will do for now (raceing)
        node_proc.terminate()
        node_proc.wait()
        print("...child killed")


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
