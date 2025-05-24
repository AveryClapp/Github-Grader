import requests
import os
from dotenv import load_dotenv
from collector import PopularityData
load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_popularity_data(user,repos):
    """
    Small driver function to control popularity data
    """
    followers, following = get_follows(user)
    num_repos = 0
    stars = 0
    watchers = 0
    for repo in repos:
        num_repos += 1
        stars += get_stargazers(user, repo)
        watchers += get_watchers(user, repo)

    avg_stars = round(float(stars/num_repos),2)
    avg_watchers = round(float(watchers/num_repos),2)
    return PopularityData(stars, avg_stars, watchers, 
                          avg_watchers, followers, following)

def get_follows(user):
    """
    Get the follower and following metrics
    """
    response = requests.get(f'{base_url}/users/{user}', headers=headers).json()
    return {
        'followers': response.get('followers', 0),
        'following': response.get('following', 0)
    }

def get_stargazers(user, repo):
    """
    Returns total stars and average stars
    """
    response = requests.get(f'{base_url}/repos/{user}/{repo}/stargazers').json()
    if response and response[0]["login"] != user:
        return 1
    return 0

def get_watchers(user, repo):
    """
    Returns total watchers and average watchers
    excluding the user
    """
    response = requests.get(f'{base_url}/repos/{user}/{repo}/subscribers').json()
    if response and response[0]["login"] != user:
        return 1
    return 0

