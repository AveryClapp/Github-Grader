import os
import traceback
from dotenv import load_dotenv
from github_api import profile_data, popularity_data, activity_data, code_quality_data, collaboration_data
from protos import GithubGrader_pb2_grpc, GithubGrader_pb2
import grpc

load_dotenv()

class PopularityProvider(GithubGrader_pb2_grpc.PopularityServiceServicer):
    def GetPopularityData(self, request, context):
        try:
            user = request.username
            pop_data = popularity_data.get_popularity_data(user)
            
            return GithubGrader_pb2.PopularityReply(
                stars=pop_data["stars"],
                avg_stars=pop_data["avg_stars"],
                watchers=pop_data["watchers"],
                avg_watchers=pop_data["avg_watchers"],
                followers=pop_data["followers"],
                following=pop_data["following"]
            )
        except Exception as e:
            print(f"Error in GetPopularityData: {e}")
            traceback.print_exc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            raise

class ActivityProvider(GithubGrader_pb2_grpc.ActivityServiceServicer):
    def GetActivityData(self, request, context):
        try:
            user = request.username
            act_data = activity_data.get_activity_data(user)
            
            return GithubGrader_pb2.ActivityReply(
                total_commits=act_data["total_commits"],
                avg_commits_per_repo=act_data["avg_commits_per_repo"],
                recent_activity_score=act_data["recent_activity_score"],
                consistency_score=act_data["consistency_score"],
                active_days=act_data["active_days"]
            )
        except Exception as e:
            print(f"Error in GetActivityData: {e}")
            traceback.print_exc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            raise

class CodeQualityProvider(GithubGrader_pb2_grpc.CodeQualityServiceServicer):
    def GetCodeQualityData(self, request, context):
        try:
            user = request.username
            code_qual = code_quality_data.get_code_quality_data(user)
            
            return GithubGrader_pb2.CodeQualityReply(
                primary_languages=code_qual["primary_languages"],
                commit_message_quality_score=code_qual["commit_message_quality_score"],
                avg_additions_per_commit=code_qual["avg_additions_per_commit"],
                avg_deletions_per_commit=code_qual["avg_deletions_per_commit"]
            )
        except Exception as e:
            print(f"Error in GetCodeQualityData: {e}")
            traceback.print_exc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            raise

class CollaborationProvider(GithubGrader_pb2_grpc.CollaborationServiceServicer):
    def GetCollaborationData(self, request, context):
        try:
            user = request.username
            collab_data = collaboration_data.get_collaboration_data(user)
            
            return GithubGrader_pb2.CollaborationReply(
                total_prs=collab_data["total_prs"],
                merged_prs=collab_data["merged_prs"],
                pr_merge_rate=collab_data["pr_merge_rate"],
                total_issues=collab_data["total_issues"],
                closed_issues=collab_data["closed_issues"],
                issue_close_rate=collab_data["issue_close_rate"],
                avg_pr_size=collab_data["avg_pr_size"]
            )
        except Exception as e:
            print(f"Error in GetCollaborationData: {e}")
            traceback.print_exc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error: {str(e)}")
            raise
