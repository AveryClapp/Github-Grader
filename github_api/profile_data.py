import requests
import os
from dotenv import load_dotenv
from typing import Tuple, List

load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_profile_data() -> Tuple[str, List[str]]:
    """
    Small Driver function to collect profile_data and return
    it to the main collector.py file
    """
    user = get_user()
    all_repos = get_all_repos(user)
    return (user, all_repos)

def get_user() -> str:
    """
    Fetches the username associated with the github key
    """
    response = requests.get(f'{base_url}/user', headers=headers).json()
    return response.get("login", None)



def get_all_repos(user) -> List[str]:
    """
    Retrieves all public repositories and returns relevant info
    """
    response = requests.get(f'{base_url}/users/{user}/repos', 
                            headers=headers).json()
    parsed_repos = []
    for repo in response:
        parsed_repos.append(repo['name'])
    return parsed_repos
