import requests
import os
from dotenv import load_dotenv
from github_api.profile_data import get_all_repos
load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_popularity_data(user):
    """
    Small driver function to control popularity data
    Returns a dictionary that can be used to create PopularityData
    """
    repos = get_all_repos(user)
    try:
        followers_data = get_follows(user)
        followers = followers_data.get('followers', 0)
        following = followers_data.get('following', 0)
        
        num_repos = 0
        stars = 0
        watchers = 0
        
        for repo in repos:
            num_repos += 1
            stars += get_stargazers(user, repo)
            watchers += get_watchers(user, repo)

        avg_stars = round(float(stars/num_repos), 2) if num_repos > 0 else 0.0
        avg_watchers = round(float(watchers/num_repos), 2) if num_repos > 0 else 0.0
        
        return {
            'stars': stars,
            'avg_stars': avg_stars,
            'watchers': watchers,
            'avg_watchers': avg_watchers,
            'followers': followers,
            'following': following
        }
        
    except Exception as e:
        print(f"Error getting popularity data: {str(e)}")
        return {
            'stars': 0,
            'avg_stars': 0.0,
            'watchers': 0,
            'avg_watchers': 0.0,
            'followers': 0,
            'following': 0
        }

def get_follows(user):
    """
    Get the follower and following metrics
    """
    response = requests.get(f'{base_url}/users/{user}', headers=headers)
    data = response.json()
    return data.get('followers', 0), data.get('following', 0)

def get_stargazers(user, repo):
    """
    Returns total stars for a repository
    """
    try:
        response = requests.get(f'{base_url}/repos/{user}/{repo}', headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            return repo_data.get('stargazers_count', 0)
        else:
            print(f"Error fetching repo data for {repo}: {response.status_code}")
            return 0
    except Exception as e:
        print(f"Error getting stargazers for {repo}: {str(e)}")
        return 0

def get_watchers(user, repo):
    """
    Returns total watchers for a repository
    """
    try:
        response = requests.get(f'{base_url}/repos/{user}/{repo}', headers=headers)
        if response.status_code == 200:
            repo_data = response.json()
            return repo_data.get('watchers_count', 0)
        else:
            print(f"Error fetching repo data for {repo}: {response.status_code}")
            return 0
    except Exception as e:
        print(f"Error getting watchers for {repo}: {str(e)}")
        return 0

def get_repository_metrics(user, repo):
    """
    Get comprehensive repository metrics including forks, stars, watchers
    """
    try:
        response = requests.get(f'{base_url}/repos/{user}/{repo}', headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'stars': data.get('stargazers_count', 0),
                'watchers': data.get('watchers_count', 0),
                'forks': data.get('forks_count', 0),
                'size': data.get('size', 0),
                'language': data.get('language', 'Unknown'),
                'created_at': data.get('created_at', ''),
                'updated_at': data.get('updated_at', ''),
                'open_issues': data.get('open_issues_count', 0)
            }
        else:
            print(f"Error fetching detailed repo data for {repo}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error getting repository metrics for {repo}: {str(e)}")
        return {}
