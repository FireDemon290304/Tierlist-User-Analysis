# -*- coding: utf-8 -*-# 
"""
Created on Sun Jul  6 08:58:30 2025

@author: Faith

Public interface.
"""

from python_js_interface import js_fetch_interface

def main():
    print("Hello World!")
    
    url = 'https://tiermaker.com/list/hollow-knight/hollow-knight-areas-51862/109401'
    logs = js_fetch_interface(url)
    print(logs)


if __name__ == "__main__":
    main()
