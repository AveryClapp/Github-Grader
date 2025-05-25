import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List
from github_api.profile_data import get_all_repos
load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_repo_commits(owner, repo, per_page=100, max_pages=3):
    """
    Gets recent commits from a Github repository
    """
    commits = []
    page = 1
    while page <= max_pages:
        try:
            response = requests.get(f'{base_url}/repos/{owner}/{repo}/commits', 
                                  headers=headers, 
                                  params={'per_page': per_page, 'page': page})
            if response.status_code != 200:
                print(f"Error fetching commits for {repo}: {response.status_code}")
                break
                
            page_commits = response.json()
            if not page_commits:
                break
            
            for commit in page_commits:
                commit_data = commit.get('commit', {})
                stats = commit.get('stats', {})
                
                parsed_commit = {
                    'message': commit_data.get('message', ''),
                    'additions': stats.get('additions', 0),
                    'deletions': stats.get('deletions', 0),
                    'date': commit_data.get('author', {}).get('date', ''),
                    'sha': commit.get('sha', '')
                }
                commits.append(parsed_commit)
            page += 1
        except Exception as e:
            print(f"Error processing commits for {repo}: {str(e)}")
            break
    
    return commits

def get_activity_data(user: str):
    """
    Analyzes user's commit activity patterns and returns activity metrics
    Returns a dictionary that can be used to create ActivityData
    """
    repos = get_all_repos(user)
    try:
        all_commits = []
        total_commits = 0
        
        for repo in repos:
            repo_commits = get_repo_commits(user, repo, per_page=100, max_pages=5)
            all_commits.extend(repo_commits)
            total_commits += len(repo_commits)
        
        if not repos:
            return {
                'total_commits': 0,
                'avg_commits_per_repo': 0.0,
                'recent_activity_score': 0,
                'consistency_score': 0.0,
                'active_days': 0
            }
        
        avg_commits_per_repo = round(total_commits / len(repos), 2)
        recent_activity_score = calculate_recent_activity(all_commits)
        consistency_score = calculate_consistency_score(all_commits)
        active_days = calculate_active_days(all_commits, days=90)
        
        return {
            'total_commits': total_commits,
            'avg_commits_per_repo': avg_commits_per_repo,
            'recent_activity_score': recent_activity_score,
            'consistency_score': consistency_score,
            'active_days': active_days
        }
        
    except Exception as e:
        print(f"Error getting activity data: {str(e)}")
        return {
            'total_commits': 0,
            'avg_commits_per_repo': 0.0,
            'recent_activity_score': 0,
            'consistency_score': 0.0,
            'active_days': 0
        }

def calculate_recent_activity(commits: List[dict], days: int = 30) -> int:
    """
    Counts commits in the last N days
    """
    if not commits:
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_commits = 0
    
    for commit in commits:
        try:
            if commit.get('date'):
                commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                if commit_date.replace(tzinfo=None) > cutoff_date:
                    recent_commits += 1
        except (ValueError, TypeError):
            continue
    
    return recent_commits

def calculate_consistency_score(commits: List[dict]) -> float:
    """
    Calculates consistency score based on commit frequency patterns
    Higher score = more consistent commit patterns
    """
    if len(commits) < 7:  
        return 0.0
    
    commit_dates = {}
    for commit in commits:
        try:
            if commit.get('date'):
                commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                date_key = commit_date.date()
                commit_dates[date_key] = commit_dates.get(date_key, 0) + 1
        except (ValueError, TypeError):
            continue
    
    if not commit_dates:
        return 0.0
    
    dates = list(commit_dates.keys())
    if len(dates) < 2:
        return 0.0
    
    dates.sort()
    date_range = (dates[-1] - dates[0]).days + 1
    
    active_days = len(dates)
    activity_rate = active_days / max(date_range, 1)
    
    daily_commits = list(commit_dates.values())
    if len(daily_commits) > 1:
        mean_commits = sum(daily_commits) / len(daily_commits)
        variance = sum((x - mean_commits) ** 2 for x in daily_commits) / len(daily_commits)
        consistency_factor = 1 / (1 + variance) 
    else:
        consistency_factor = 1.0
    
    consistency_score = (activity_rate * 0.7 + consistency_factor * 0.3) * 100
    
    return round(min(100.0, consistency_score), 2)

def calculate_active_days(commits: List[dict], days: int = 90) -> int:
    """
    Counts unique days with at least one commit in the last N days
    """
    if not commits:
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    active_dates = set()
    
    for commit in commits:
        try:
            if commit.get('date'):
                commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                if commit_date.replace(tzinfo=None) > cutoff_date:
                    active_dates.add(commit_date.date())
        except (ValueError, TypeError):
            continue
    
    return len(active_dates)

def get_commit_frequency_stats(user: str, repos: List[str]) -> dict:
    """
    Additional helper function to get detailed commit frequency statistics
    """
    try:
        all_commits = []
        for repo in repos:
            repo_commits = get_repo_commits(user, repo, per_page=50, max_pages=3)
            all_commits.extend(repo_commits)
        
        if not all_commits:
            return {
                'commits_per_week': 0,
                'commits_per_month': 0,
                'total_analyzed': 0
            }
        
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        commits_this_week = 0
        commits_this_month = 0
        
        for commit in all_commits:
            try:
                if commit.get('date'):
                    commit_date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                    commit_date = commit_date.replace(tzinfo=None)
                    
                    if commit_date > week_ago:
                        commits_this_week += 1
                    if commit_date > month_ago:
                        commits_this_month += 1
            except (ValueError, TypeError):
                continue
        
        return {
            'commits_per_week': commits_this_week,
            'commits_per_month': commits_this_month,
            'total_analyzed': len(all_commits)
        }
        
    except Exception as e:
        print(f"Error getting commit frequency stats: {str(e)}")
        return {
            'commits_per_week': 0,
            'commits_per_month': 0,
            'total_analyzed': 0
        }
