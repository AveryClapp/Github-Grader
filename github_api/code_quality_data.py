import requests
import os
import re
from dotenv import load_dotenv
from typing import List, Dict
from .activity_data import get_repo_commits
from github_api.profile_data import get_all_repos
load_dotenv()
github_key = os.getenv("GITHUB_KEY")
headers = {'Authorization': f'token {github_key}'}
base_url = 'https://api.github.com'

def get_repo_languages(owner, repo):
    """
    Returns the language distribution in the repository
    """
    try:
        response = requests.get(f'{base_url}/repos/{owner}/{repo}/languages', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching languages for {repo}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error getting languages for {repo}: {str(e)}")
        return {}

def analyze_commit_message_quality(messages):
    """
    Analyzes commit messages and returns a quality score 0-100
    """
    if not messages:
        return 0.0
    
    total_score = 0
    for message in messages:
        score = score_single_commit_message(message)
        total_score += score
    
    return round(total_score / len(messages), 2)

def score_single_commit_message(message):
    """
    Scores a single commit message based on quality indicators
    """
    if not message or len(message.strip()) == 0:
        return 0
    
    message = message.strip()
    score = 0
    
    if len(message) >= 50:
        score += 25
    elif len(message) >= 20:
        score += 15
    elif len(message) >= 10:
        score += 10
    else:
        score += 5

    if message[0].isupper():
        score += 15
    
    action_verbs = ['add', 'fix', 'update', 'remove', 'refactor', 'implement', 
                   'create', 'delete', 'modify', 'improve', 'optimize']
    first_word = message.split()[0].lower()
    if first_word in action_verbs:
        score += 20
    
    lazy_patterns = ['wip', 'test', 'asdf', 'update', 'fix', 'changes', 'stuff']
    if message.lower() in lazy_patterns:
        score -= 10
    elif len(message.split()) >= 3:
        score += 15
    
    conventional_pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'
    if re.match(conventional_pattern, message, re.IGNORECASE):
        score += 20
    
    return max(0, min(100, score))

def get_code_quality_data(user: str):
    """
    Analyzes code quality metrics across user's repositories
    Returns a dictionary that can be used to create CodeQualityData
    """
    repos = get_all_repos(user)
    try:
        all_languages = {}
        all_commit_messages = []
        total_additions = 0
        total_deletions = 0
        total_commits_with_stats = 0
        
        for repo in repos:
            repo_languages = get_repo_languages(user, repo)
            for lang, bytes_count in repo_languages.items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count
            
            repo_commits = get_repo_commits(user, repo, per_page=50, max_pages=3)
            for commit in repo_commits:
                if commit.get('message'):
                    all_commit_messages.append(commit['message'])
                
                if commit.get('additions') or commit.get('deletions'):
                    total_additions += commit.get('additions', 0)
                    total_deletions += commit.get('deletions', 0)
                    total_commits_with_stats += 1
        
        commit_message_quality_score = analyze_commit_message_quality(all_commit_messages)
        
        avg_additions_per_commit = (
            round(total_additions / total_commits_with_stats, 2) 
            if total_commits_with_stats > 0 else 0.0
        )
        
        avg_deletions_per_commit = (
            round(total_deletions / total_commits_with_stats, 2) 
            if total_commits_with_stats > 0 else 0.0
        )
        
        language_diversity_score = len(all_languages)
        
        return {
            'primary_languages': all_languages,
            'commit_message_quality_score': commit_message_quality_score,
            'avg_additions_per_commit': avg_additions_per_commit,
            'avg_deletions_per_commit': avg_deletions_per_commit,
            'language_diversity_score': language_diversity_score
        }
        
    except Exception as e:
        print(f"Error getting code quality data: {str(e)}")
        return {
            'primary_languages': {},
            'commit_message_quality_score': 0.0,
            'avg_additions_per_commit': 0.0,
            'avg_deletions_per_commit': 0.0,
            'language_diversity_score': 0
        }

def get_repository_structure_score(user: str, repo: str) -> float:
    """
    Analyzes repository structure for quality indicators
    """
    try:
        important_files = ['README.md', 'LICENSE', 'requirements.txt', 
            'package.json', 'Cargo.toml', 'pom.xml', 'setup.py', '.gitignore']
        
        found_files = 0
        for file in important_files:
            response = requests.get(f'{base_url}/repos/{user}/{repo}/contents/{file}', 
                                  headers=headers)
            if response.status_code == 200:
                found_files += 1
        
        response = requests.get(f'{base_url}/repos/{user}/{repo}/contents', headers=headers)
        if response.status_code == 200:
            contents = response.json()
            directories = [item for item in contents if item.get('type') == 'dir']
            
            good_dirs = ['src', 'lib', 'docs', 'test', 'tests', 'examples', 'scripts']
            good_dirs_found = sum(1 for d in directories if d.get('name', '').lower() in good_dirs)
            
            structure_score = (found_files * 10) + (good_dirs_found * 5)
            return min(100.0, structure_score)
        
        return found_files * 10
        
    except Exception as e:
        print(f"Error analyzing repository structure for {repo}: {str(e)}")
        return 0.0

def get_language_quality_indicators(languages: Dict[str, int]) -> Dict[str, any]:
    """
    Analyzes language usage patterns for quality indicators
    """
    if not languages:
        return {
            'dominant_language': None,
            'language_balance': 0.0,
            'modern_languages_ratio': 0.0
        }
    
    sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    total_bytes = sum(languages.values())
    
    dominant_language = sorted_languages[0][0] if sorted_languages else None
    
    if len(languages) > 1:
        percentages = [bytes_count / total_bytes for bytes_count in languages.values()]
        balance = -sum(p * (p.bit_length() - 1) for p in percentages if p > 0) / len(languages)
        language_balance = round(balance, 3)
    else:
        language_balance = 0.0
    
    modern_languages = {
        'Python', 'JavaScript', 'TypeScript', 'Rust', 'Go', 'Kotlin', 
        'Swift', 'Dart', 'Julia', 'React', 'Vue', 'Svelte'
    }
    
    modern_bytes = sum(bytes_count for lang, bytes_count in languages.items() 
                      if lang in modern_languages)
    modern_languages_ratio = round(modern_bytes / total_bytes, 3) if total_bytes > 0 else 0.0
    
    return {
        'dominant_language': dominant_language,
        'language_balance': language_balance,
        'modern_languages_ratio': modern_languages_ratio,
        'total_languages': len(languages)
    }

def calculate_overall_code_quality_score(code_quality_dict: dict) -> float:
    """
    Calculates an overall code quality score from 0-100
    """
    try:
        score = 0.0
        
        score += code_quality_dict.get('commit_message_quality_score', 0) * 0.4
        
        diversity_score = min(20, code_quality_dict.get('language_diversity_score', 0) * 4)
        score += diversity_score
        
        avg_changes = (code_quality_dict.get('avg_additions_per_commit', 0) + 
                      code_quality_dict.get('avg_deletions_per_commit', 0))
        if 10 <= avg_changes <= 200:
            size_score = 20
        elif 5 <= avg_changes <= 500:
            size_score = 15
        elif avg_changes > 0:
            size_score = 10
        else:
            size_score = 0
        score += size_score
        
        lang_indicators = get_language_quality_indicators(code_quality_dict.get('primary_languages', {}))
        modern_ratio = lang_indicators.get('modern_languages_ratio', 0)
        score += modern_ratio * 20
        
        return round(min(100.0, score), 2)
        
    except Exception as e:
        print(f"Error calculating overall code quality score: {str(e)}")
        return 0.0
