# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 09:10:54 2025

@author: Faith
"""

import subprocess
import requests
import time
import os


local = "http://localhost:3000"
base = "https://tiermaker.com"


def stream_sub_urls(path: str, base_url: str):
    """
    Reads a file of URL paths line by line, prepends the base URL,
    and yields them as newline-terminated byte strings for streaming.
    This is a generator, so it uses minimal memory.
    """

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            # Assuming the file contains one relative path per line
            clean_path = line.strip().strip('"')
            if clean_path:
                # Append a newline to each URL so the Node server's readline works correctly
                full_url = base_url + clean_path + '\n'
                yield full_url.encode('utf-8')


def start_server():
    print("Spawning Node.js child process...")
    # Use Popen to run the server in the background
    node_server = subprocess.Popen(['node', 'js/server.js'])
    # Give the server a moment to initialize
    time.sleep(2)
    print("\t...child process started.")
    return node_server


def fetch(mainpage_url: str, dataDir: str, name: str) -> None:
    node_proc = start_server()
    print(f'Starting fetch for {name}')
    try:
        main_links_file = os.path.join(dataDir, f"{name}_main_links.jsonl")
        sub_data_file = os.path.join(dataDir, f"{name}_sub_data.jsonl")

        print("Getting main page links")
        main_res = requests.post(
            local + '/scrape',
            data=mainpage_url.encode('utf-8'),
            headers={
                'Content-Type': 'text/plain',
                'X-Is-Main': 'true',
                'X-Outfile': main_links_file,
                'X-Verbose': 'true'
            }
        )
        main_res.raise_for_status()
        print("\t...main links saved.")

        print("Streaming sub-page links for individual scraping...")

        sub_res = requests.post(
            local + '/scrape',
            data=stream_sub_urls(main_links_file, base),
            headers={
                'Content-Type': 'application/x-ndjson',
                'X-Is-Main': 'false',
                'X-Outfile': sub_data_file,
                'X-Verbose': 'false'
            }
        )
        sub_res.raise_for_status()
        print("\t...individual entries done.")
    except requests.exceptions.RequestException as e:
        print(f"\nAn error occurred during an HTTP request: {e}")
    finally:
        # --- SHUTDOWN ---
        print("\t...fetch process complete. Stopping server...")
        try:
            requests.post(local + '/stop')
        except requests.exceptions.ConnectionError:
            print("\t...server was already down.")

        # Wait a moment for the server to close before terminating the process
        time.sleep(1)
        node_proc.terminate()
        node_proc.wait()
        print("...child killed: Done fetching.")


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
