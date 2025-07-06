# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 09:10:54 2025

@author: Faith
"""

import subprocess

def js_fetch_interface(url):
    print("fetching...")
    
    result = subprocess.run(
        ['node', 'js/fetch.js', url, 'data/fetchResult.json'],
        capture_output=True,
        text=True)
    if result.returncode != 0:
        print("error")
        print(result.stderr)
        return None
    
    print("Fetched!")
    return result.stdout        # return logs because why not

if __name__ == "__main__":
    url = 'https://tiermaker.com/list/hollow-knight/hollow-knight-areas-51862/2245367'
    response = js_fetch_interface(url)
    if response:
        print("js logs:\n", response)


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
