import requests
import os
from dotenv import load_dotenv

load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'
