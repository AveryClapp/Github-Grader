import grpc
from concurrent import futures
from protos import GithubGrader_pb2_grpc
from collector import PopularityProvider, ActivityProvider, CodeQualityProvider, CollaborationProvider


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
GithubGrader_pb2_grpc.add_ActivityServiceServicer_to_server(ActivityProvider(), server)  
GithubGrader_pb2_grpc.add_PopularityServiceServicer_to_server(PopularityProvider(), server)  
GithubGrader_pb2_grpc.add_CodeQualityServiceServicer_to_server(CodeQualityProvider(), server)
GithubGrader_pb2_grpc.add_CollaborationServiceServicer_to_server(CollaborationProvider(), server)

server.add_insecure_port('[::]:5005')
server.start()
server.wait_for_termination()
