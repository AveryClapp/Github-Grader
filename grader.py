import sys
import grpc
import concurrent.futures
from protos import GithubGrader_pb2, GithubGrader_pb2_grpc

def fetch_activity_data(channel, username):
    stub = GithubGrader_pb2_grpc.ActivityServiceStub(channel)
    request = GithubGrader_pb2.ActivityRequest(username=username)
    return stub.GetActivityData(request)

def fetch_popularity_data(channel, username):
    stub = GithubGrader_pb2_grpc.PopularityServiceStub(channel)
    request = GithubGrader_pb2.PopularityRequest(username=username)
    return stub.GetPopularityData(request)

def fetch_code_quality_data(channel, username):
    stub = GithubGrader_pb2_grpc.CodeQualityServiceStub(channel)
    request = GithubGrader_pb2.CodeQualityRequest(username=username)
    return stub.GetCodeQualityData(request)

def fetch_collaboration_data(channel, username):
    stub = GithubGrader_pb2_grpc.CollaborationServiceStub(channel)
    request = GithubGrader_pb2.CollaborationRequest(username=username)
    return stub.GetCollaborationData(request)

def calculate_grade(activity, popularity, code_quality, collaboration):
    total_score = 0.0
    weights = {'activity': 0.35, 'popularity': 0.20, 'code_quality': 0.30, 'collaboration': 0.15}
    
    activity_score = 0.0
    if activity.total_commits > 0:
        commit_score = min(100, activity.total_commits / 10)
        consistency_score = activity.consistency_score
        recent_activity_score = min(100, activity.recent_activity_score * 3.33)
        active_days_score = min(100, activity.active_days * 1.11)
        activity_score = (commit_score * 0.25 + consistency_score * 0.35 + 
                         recent_activity_score * 0.25 + active_days_score * 0.15)
    
    popularity_score = 0.0
    if popularity.stars > 0 or popularity.followers > 0:
        star_score = min(100, popularity.avg_stars * 5)
        follower_score = min(100, popularity.followers * 0.5)
        watcher_score = min(100, popularity.avg_watchers * 10)
        popularity_score = (star_score * 0.5 + follower_score * 0.3 + watcher_score * 0.2)
    
    code_quality_score = 0.0
    if code_quality.commit_message_quality_score > 0:
        message_score = code_quality.commit_message_quality_score
        language_diversity = min(100, len(code_quality.primary_languages) * 15)
        change_size_score = 0
        avg_changes = code_quality.avg_additions_per_commit + code_quality.avg_deletions_per_commit
        if 10 <= avg_changes <= 200:
            change_size_score = 100
        elif 5 <= avg_changes <= 500:
            change_size_score = 75
        elif avg_changes > 0:
            change_size_score = 50
        code_quality_score = (message_score * 0.5 + language_diversity * 0.3 + change_size_score * 0.2)
    
    collaboration_score = 0.0
    if collaboration.total_prs > 0 or collaboration.total_issues > 0:
        pr_rate_score = collaboration.pr_merge_rate * 100
        issue_rate_score = collaboration.issue_close_rate * 100
        pr_activity_score = min(100, collaboration.total_prs * 5)
        issue_activity_score = min(100, collaboration.total_issues * 5)
        collaboration_score = (pr_rate_score * 0.3 + issue_rate_score * 0.3 + 
                              pr_activity_score * 0.2 + issue_activity_score * 0.2)
    
    total_score = (activity_score * weights['activity'] + 
                   popularity_score * weights['popularity'] + 
                   code_quality_score * weights['code_quality'] + 
                   collaboration_score * weights['collaboration'])
    
    if total_score >= 90:
        grade = "A+"
    elif total_score >= 85:
        grade = "A"
    elif total_score >= 80:
        grade = "A-"
    elif total_score >= 75:
        grade = "B+"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 65:
        grade = "B-"
    elif total_score >= 60:
        grade = "C+"
    elif total_score >= 55:
        grade = "C"
    elif total_score >= 50:
        grade = "C-"
    elif total_score >= 40:
        grade = "D"
    else:
        grade = "F"
    
    return {
        'total_score': round(total_score, 2),
        'grade': grade,
        'breakdown': {
            'activity': round(activity_score, 2),
            'popularity': round(popularity_score, 2),
            'code_quality': round(code_quality_score, 2),
            'collaboration': round(collaboration_score, 2)
        }
    }

def main():
    channel = grpc.insecure_channel('localhost:5005')
    username = sys.argv[-1]
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_activity = executor.submit(fetch_activity_data, channel, username)
            future_popularity = executor.submit(fetch_popularity_data, channel, username)
            future_code_quality = executor.submit(fetch_code_quality_data, channel, username)
            future_collaboration = executor.submit(fetch_collaboration_data, channel, username)
            
            activity_response = future_activity.result()
            popularity_response = future_popularity.result()
            code_quality_response = future_code_quality.result()
            collaboration_response = future_collaboration.result()
        
        print(f"\n{'='*60}")
        print(f"GitHub Profile Analysis for: {username}")
        print(f"{'='*60}\n")
        
        print("Activity Metrics:")
        print(f"  Total Commits: {activity_response.total_commits}")
        print(f"  Consistency Score: {activity_response.consistency_score:.1f}%")
        print(f"  Recent Activity: {activity_response.recent_activity_score} commits (last 30 days)")
        print(f"  Active Days: {activity_response.active_days} (last 90 days)\n")
        
        print("Popularity Metrics:")
        print(f"  Total Stars: {popularity_response.stars}")
        print(f"  Average Stars per Repo: {popularity_response.avg_stars:.1f}")
        print(f"  Followers: {popularity_response.followers}\n")
        
        print("Code Quality Metrics:")
        print(f"  Commit Message Quality: {code_quality_response.commit_message_quality_score:.1f}%")
        print(f"  Languages Used: {len(code_quality_response.primary_languages)}")
        print(f"  Avg Changes per Commit: {code_quality_response.avg_additions_per_commit + code_quality_response.avg_deletions_per_commit:.1f} lines\n")
        
        print("Collaboration Metrics:")
        print(f"  Pull Requests: {collaboration_response.total_prs} (Merge Rate: {collaboration_response.pr_merge_rate:.1%})")
        print(f"  Issues: {collaboration_response.total_issues} (Close Rate: {collaboration_response.issue_close_rate:.1%})\n")
        
        result = calculate_grade(activity_response, popularity_response, 
                               code_quality_response, collaboration_response)
        
        print(f"{'='*60}")
        print(f"FINAL GRADE: {result['grade']} ({result['total_score']:.1f}/100)")
        print(f"{'='*60}\n")
        
        print("Score Breakdown:")
        print(f"  Activity:      {result['breakdown']['activity']:6.1f}/100 (35%)")
        print(f"  Code Quality:  {result['breakdown']['code_quality']:6.1f}/100 (30%)")
        print(f"  Popularity:    {result['breakdown']['popularity']:6.1f}/100 (20%)")
        print(f"  Collaboration: {result['breakdown']['collaboration']:6.1f}/100 (15%)")
        
    except grpc.RpcError as e:
        print(f"RPC failed: {e}")
    finally:
        channel.close()

if __name__ == '__main__':
    main()
