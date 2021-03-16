from __future__ import print_function
import logging
import sys

sys.path.append('grpc_packages')

import grpc
import Manage_pb2 as Manager
import Manage_pb2_grpc as Manager_grpc
def GetFile():
    with grpc.insecure_channel('localhost:8666') as channel:
        # 客户端通过stub来实现rpc通信
        stub = Manager_grpc.ContainerManagerStub(channel)
        request = Manager.GetFile_Request(\
            container_id = 'container1',
            path = '/workplace/test.py'
        )
        # 客户端必须使用定义好的类型，这里是HelloRequest类型
        response = stub.GetFile(request=request)
        file = open("test.tar", "wb+")
        for Data in response:
            file.write(Data.data)
        file.close()

def test_BuildImage():
    with grpc.insecure_channel('0.0.0.0:8666') as channel:
        # 客户端通过stub来实现rpc通信
        stub = Manager_grpc.ManagerStub(channel)
        file = open("dockerfile","rb")
        dockerfile = file.read()
        request = Manager.BuildImage_Request(
            dockerfile = dockerfile,
            tag = "test:v2.0"
        )
        # 客户端必须使用定义好的类型，这里是HelloRequest类型
        response = stub.BuildImage(request=request)
        print ("hello client received: " , response.exit_code)

def GenerateData(List):
    for temp in List:
        yield temp
def run():
    # 使用with语法保证channel自动close
    with grpc.insecure_channel('0.0.0.0:8666') as channel:
        # 客户端通过stub来实现rpc通信
        stub = Manager_grpc.ManagerStub(channel)
        request = Manager.ListContainers_Request()
        # 客户端必须使用定义好的类型，这里是HelloRequest类型
        response = stub.ListContainers(request=request)
        print ("hello client received: " )
# 1613637295
if __name__ == "__main__":
    logging.basicConfig()
    # run()
    test_BuildImage()