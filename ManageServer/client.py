from __future__ import print_function
import logging

import grpc
import Manage_pb2 as Manager
import Manage_pb2_grpc as Manager_grpc

def run():
    # 使用with语法保证channel自动close
    with grpc.insecure_channel('localhost:8666') as channel:
        # 客户端通过stub来实现rpc通信
        stub = Manager_grpc.ContainerManagerStub(channel)
        temp = Manager.GetArchive_Request(
            container_id = 'container1',
            path = "/etc/apt/sources.list"
        )
        # 客户端必须使用定义好的类型，这里是HelloRequest类型
        response = stub.GetArchive(temp)
        file = open("temp.list","wb+")
        for data in response:
            file.write(data.data)
    # print ("hello client received: " + response.container_id)

if __name__ == "__main__":
    logging.basicConfig()
    run()