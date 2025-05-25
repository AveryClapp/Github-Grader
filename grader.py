import sys
import grpc
from protos import GithubGrader_pb2, GithubGrader_pb2_grpc

def main():
    channel = grpc.insecure_channel('localhost:5005')
    username = sys.argv[-1]
    popularity_stub = GithubGrader_pb2_grpc.PopularityServiceStub(channel)
    code_quality_stub = GithubGrader_pb2_grpc.CodeQualityServiceStub(channel)
    collaboration_stub = GithubGrader_pb2_grpc.CollaborationServiceStub(channel)
    activity_stub = GithubGrader_pb2_grpc.ActivityServiceStub(channel)

    try:
        activity_request = GithubGrader_pb2.ActivityRequest(username=username)
        activity_response = activity_stub.GetActivityData(activity_request)
        print(f"Activity: {activity_response}")

        popularity_request = GithubGrader_pb2.PopularityRequest(username=username)
        popularity_response = popularity_stub.GetPopularityData(popularity_request)
        print(f"Popularity: {popularity_response}")

        code_request = GithubGrader_pb2.CodeQualityRequest(username=username)
        code_response = code_quality_stub.GetCodeQualityData(code_request)
        print(f"Code Quality: {code_response}")

        collab_request = GithubGrader_pb2.CollaborationRequest(username=username)
        collab_response = collaboration_stub.GetCollaborationData(collab_request)
        print(f"Collaboration: {collab_response}")

    except grpc.RpcError as e:
        print(f"RPC failed: {e}")

    channel.close()

if __name__ == '__main__':
    main()


