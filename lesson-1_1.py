from __future__ import print_function
import requests
import os
from dotenv import load_dotenv

load_dotenv(r"C:\Users\vschitov\Desktop\Python\lesson\ParsingData\.env")

owner = "Schitov"
access_token = os.getenv("ACCESS_TOKEN")

headers = {'Authorization':"Token "+access_token}
url = f"https://api.github.com/users/{owner}/repos"
repo = requests.get(url, headers=headers).json()

for el in repo:
    print(el["name"])
