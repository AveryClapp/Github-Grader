import requests
import os
from dotenv import load_dotenv
from typing import List
from github_api.profile_data import get_all_repos
load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_pull_requests(owner, repo):
    """
    Returns relevant information on pull requests in a repo
    """
    try:
        response = requests.get(f'{base_url}/repos/{owner}/{repo}/pulls', 
                              headers=headers, 
                              params={'state': 'all', 'per_page': 100})
        
        if response.status_code != 200:
            print(f"Error fetching PRs for {repo}: {response.status_code}")
            return []
            
        prs = response.json()
        parsed_prs = []
        
        for pr in prs:
            parsed_prs.append({
                'state': pr.get('state'),
                'additions': pr.get('additions', 0),
                'deletions': pr.get('deletions', 0),
                'changed_files': pr.get('changed_files', 0),
                'merged': pr.get('merged', False),
                'comments': pr.get('comments', 0)
            })
        return parsed_prs
        
    except Exception as e:
        print(f"Error processing PRs for {repo}: {str(e)}")
        return []

def get_issues(owner, repo):
    """
    Returns the issues on user's public repositories
    """
    try:
        response = requests.get(f'{base_url}/repos/{owner}/{repo}/issues', 
                              headers=headers, 
                              params={'state': 'all', 'per_page': 100})
        
        if response.status_code != 200:
            print(f"Error fetching issues for {repo}: {response.status_code}")
            return []
            
        issues = response.json()
        parsed_issues = []
        
        for issue in issues:
            if not issue.get('pull_request'):
                parsed_issues.append({
                    'state': issue.get('state'),
                    'comments': issue.get('comments', 0),
                    'closed': issue.get('state') == 'closed'
                })
        return parsed_issues
        
    except Exception as e:
        print(f"Error processing issues for {repo}: {str(e)}")
        return []

def get_collaboration_data(user: str):
    """
    Analyzes collaboration patterns across user's repositories
    Returns a dictionary that can be used to create CollaborationData
    """
    repos = get_all_repos(user)
    try:
        total_prs = 0
        merged_prs = 0
        total_issues = 0
        closed_issues = 0
        pr_size_sum = 0
        pr_with_size_count = 0
        community_score = 0
        
        for repo in repos:
            repo_prs = get_pull_requests(user, repo)
            total_prs += len(repo_prs)
            
            for pr in repo_prs:
                if pr.get('merged') or pr.get('state') == 'closed':
                    merged_prs += 1
                
                pr_size = pr.get('additions', 0) + pr.get('deletions', 0)
                if pr_size > 0:
                    pr_size_sum += pr_size
                    pr_with_size_count += 1
                
                community_score += pr.get('comments', 0)
            
            repo_issues = get_issues(user, repo)
            total_issues += len(repo_issues)
            
            for issue in repo_issues:
                if issue.get('closed') or issue.get('state') == 'closed':
                    closed_issues += 1
                
                community_score += issue.get('comments', 0)
        
        pr_merge_rate = (
            round(merged_prs / total_prs, 3) if total_prs > 0 else 0.0
        )
        
        issue_close_rate = (
            round(closed_issues / total_issues, 3) if total_issues > 0 else 0.0
        )
        
        avg_pr_size = (
            round(pr_size_sum / pr_with_size_count, 2) if pr_with_size_count > 0 else 0.0
        )
        
        community_engagement_score = (
            round(community_score / len(repos), 1) if repos else 0
        )
        
        return {
            'total_prs': total_prs,
            'merged_prs': merged_prs,
            'pr_merge_rate': pr_merge_rate,
            'total_issues': total_issues,
            'closed_issues': closed_issues,
            'issue_close_rate': issue_close_rate,
            'avg_pr_size': avg_pr_size,
            'community_engagement_score': community_engagement_score
        }
        
    except Exception as e:
        print(f"Error getting collaboration data: {str(e)}")
        return {
            'total_prs': 0,
            'merged_prs': 0,
            'pr_merge_rate': 0.0,
            'total_issues': 0,
            'closed_issues': 0,
            'issue_close_rate': 0.0,
            'avg_pr_size': 0.0,
            'community_engagement_score': 0
        }

def get_collaboration_quality_score(collaboration_dict: dict) -> float:
    """
    Calculates an overall collaboration quality score from 0-100
    """
    try:
        score = 0.0
        
        pr_merge_rate = collaboration_dict.get('pr_merge_rate', 0)
        if pr_merge_rate >= 0.8:
            score += 30
        elif pr_merge_rate >= 0.6:
            score += 25
        elif pr_merge_rate >= 0.4:
            score += 20
        elif pr_merge_rate > 0:
            score += 10
        
        issue_close_rate = collaboration_dict.get('issue_close_rate', 0)
        if issue_close_rate >= 0.8:
            score += 25
        elif issue_close_rate >= 0.6:
            score += 20
        elif issue_close_rate >= 0.4:
            score += 15
        elif issue_close_rate > 0:
            score += 10
        
        total_prs = collaboration_dict.get('total_prs', 0)
        total_issues = collaboration_dict.get('total_issues', 0)
        total_activity = total_prs + total_issues
        
        if total_activity >= 50:
            score += 25
        elif total_activity >= 20:
            score += 20
        elif total_activity >= 10:
            score += 15
        elif total_activity >= 5:
            score += 10
        elif total_activity > 0:
            score += 5

        engagement = collaboration_dict.get('community_engagement_score', 0)
        if engagement >= 10:
            score += 20
        elif engagement >= 5:
            score += 15
        elif engagement >= 2:
            score += 10
        elif engagement > 0:
            score += 5
        
        return round(min(100.0, score), 2)
        
    except Exception as e:
        print(f"Error calculating collaboration quality score: {str(e)}")
        return 0.0

def analyze_contribution_patterns(user: str, repos: List[str]) -> dict:
    """
    Analyzes patterns in user's contributions to understand collaboration style
    """
    try:
        contribution_data = {
            'avg_pr_comments': 0.0,
            'avg_issue_comments': 0.0,
            'pr_size_distribution': {'small': 0, 'medium': 0, 'large': 0},
            'collaboration_style': 'unknown'
        }
        
        total_pr_comments = 0
        total_prs = 0
        total_issue_comments = 0
        total_issues = 0
        
        for repo in repos:
            prs = get_pull_requests(user, repo)
            for pr in prs:
                total_prs += 1
                total_pr_comments += pr.get('comments', 0)
                
                pr_size = pr.get('additions', 0) + pr.get('deletions', 0)
                if pr_size < 50:
                    contribution_data['pr_size_distribution']['small'] += 1
                elif pr_size < 200:
                    contribution_data['pr_size_distribution']['medium'] += 1
                else:
                    contribution_data['pr_size_distribution']['large'] += 1
            
            issues = get_issues(user, repo)
            for issue in issues:
                total_issues += 1
                total_issue_comments += issue.get('comments', 0)
        
        if total_prs > 0:
            contribution_data['avg_pr_comments'] = round(total_pr_comments / total_prs, 2)
        
        if total_issues > 0:
            contribution_data['avg_issue_comments'] = round(total_issue_comments / total_issues, 2)
        
        avg_comments = (contribution_data['avg_pr_comments'] + 
                       contribution_data['avg_issue_comments']) / 2
        
        if avg_comments >= 5:
            contribution_data['collaboration_style'] = 'highly_collaborative'
        elif avg_comments >= 2:
            contribution_data['collaboration_style'] = 'collaborative'
        elif avg_comments >= 0.5:
            contribution_data['collaboration_style'] = 'moderately_collaborative'
        else:
            contribution_data['collaboration_style'] = 'independent'
        
        return contribution_data
        
    except Exception as e:
        print(f"Error analyzing contribution patterns: {str(e)}")
        return {
            'avg_pr_comments': 0.0,
            'avg_issue_comments': 0.0,
            'pr_size_distribution': {'small': 0, 'medium': 0, 'large': 0},
            'collaboration_style': 'unknown'
        }

def get_external_contributions(user: str) -> dict:
    """
    Attempts to find contributions to repositories not owned by the user
    This gives insight into open source collaboration
    """
    try:
        response = requests.get(f'{base_url}/users/{user}/events', 
                              headers=headers, 
                              params={'per_page': 100})
        
        if response.status_code != 200:
            return {'external_contributions': 0, 'contributed_repos': []}
        
        events = response.json()
        external_contributions = 0
        contributed_repos = set()
        
        for event in events:
            if event.get('type') in ['PullRequestEvent', 'IssuesEvent', 'PushEvent']:
                repo_info = event.get('repo', {})
                repo_name = repo_info.get('name', '')
                
                if repo_name and not repo_name.startswith(f"{user}/"):
                    external_contributions += 1
                    contributed_repos.add(repo_name)
        
        return {
            'external_contributions': external_contributions,
            'contributed_repos': list(contributed_repos),
            'unique_external_repos': len(contributed_repos)
        }
        
    except Exception as e:
        print(f"Error getting external contributions: {str(e)}")
        return {'external_contributions': 0, 'contributed_repos': [], 'unique_external_repos': 0}
