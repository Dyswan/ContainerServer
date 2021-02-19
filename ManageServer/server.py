import sys
sys.path.append('./protos')

from concurrent import futures
from utils import ContainerUtils, ImageUtils
import grpc
import Manage_pb2 as Manager
import Manage_pb2_grpc as Manager_grpc

def GenerateData(List):
    for message in List:
        yield message.data

class ContainerManagerHandler(Manager_grpc.ContainerManagerServicer ):
    def __init__(self):
        pass
    def PruneContainers(self, request,context):
        ContainerUtils.PruneContainers()
        return Manager.PruneContainers_Response()

    def ListContainers(self, request , context):
        containers = ContainerUtils.ListContainers()
        response = Manager.ListContainers_Response()
        for container in containers:
            attr = response.containers.add()
            attr.id = container['Id']
            attr.created = container['Created']
            attr.status = container['Status']
            attr.image = container['Image']
            attr.Name = container['Name']
        return response
    
    def GetContainer(self, request, context):
        ret = ContainerUtils.GetContainer(request.container_id)
        attr = Manager.GetArchive_Response()
        attr.id = container['Id']
        attr.created = container['Created']
        attr.status = container['Status']
        attr.image = container['Image']
        attr.Name = container['Name']
        return attr
    
    def CreateContainer(self, request, context):
        ret = ContainerUtils.CreateContainer(image_id= request.image_id,
                                             mount_path = "/workplace/{username}/{container_name}".format(username=request.username,container_name=request.container_name),
                                             container_name = request.container_name)
        container = Manager.CreateContainer_Response()
        container.container_id = ret
        return container
    
    def StopContainer(self, request, context):
        ContainerUtils.StopContainer(request.container_id)
        return Manager.StopContainer_Response()
    
    def RemoveContainer(self, request, context):
        ContainerUtils.StopContainer(request.container_id, request.force)
        return Manager.RemoveContainer_Response()

    def RestartContainer(self, request, context):
        ContainerUtils.RestartContainer(request.container_id)
        return Manager.RestartContainer_Response()

    def GetFile(self, request ,context):
        bits , stat = ContainerUtils.GetArchive(request.container_id, request.path)
        for data in bits:
            yield Manager.GetFile_Response(data = data)
      
    def UpdateFile(self, request ,context):
        container_id = request.container_id
        path = request.path
        file_name = request.file_name
        old_version = request.old_version
        exit_code, old_file_stat = ContainerUtils.ExecCommand(\
            container_id=container_id,
            exec_cmd = ["stat", "-c", "%Y", path+"/"+file_name]
        )
        if exit_code == 0:
            if old_version == old_file_stat or request.force:
                # generate_data = GenerateData(request)
                if not ContainerUtils.PutArchive(container_id, path, request.data):
                    return Manager.UpdateFile_Response(exit_code=Manager.UpdateFile_Response.ExitCode.UNKNOWN_ERROR)
                else:
                    exit_code, new_version = ContainerUtils.ExecCommand(\
                        container_id=container_id,
                        exec_cmd = ["stat", "-c", "%Y", path]
                    )
                    return Manager.UpdateFile_Response(\
                            exit_code = Manager.UpdateFile_Response.ExitCode.SUCCESS,
                            new_version = new_version
                        )
            else:
                return Manager.UpdateFile_Response(\
                    exit_code=Manager.UpdateFile_Response.ExitCode.MTIME_SYNC_ERROR)
        elif exit_code == 1:
            return Manager.UpdateFile_Response(\
                exit_code=Manager.UpdateFile_Response.ExitCode.FILE_IS_NOT_EXIST)
        


    
    def ListFile(self, request ,context):
        cmd = ["ls", "-Al", request.path]
        exit_code, output = ContainerUtils.ExecCommand(request.container_id, cmd)
        response = Manager.ListFile_Response()
        if exit_code == 0:
            response.exit_code = Manager.ListFile_Response.ExitCode.SUCCESS
            List = output.strip().split('\n')[1:]
            for file in List:
                temp = file.split(' ')
                stat = temp[0]
                filename = temp[-1]
                temp = response.files.add()
                temp.file_name = filename
                if stat[0] == '-':
                    temp.file_type = Manager.FileStat.FileType.FILE
                elif stat[0] == 'd':
                    temp.file_type = Manager.FileStat.FileType.FOLDER
                elif stat[0] == 'i':
                    temp.file_type = Manager.FileStat.FileType.LINK
        elif exit_code == 1:
            response.exit_code = Manager.ListFile_Response.ExitCode.MINOR_PROBLEMS
        elif exit_code == 2:
            response.exit_code = Manager.ListFile_Response.ExitCode.SERIOUS_TROUBLE
        return response
    


    
        
if __name__=="__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    Manager_grpc.add_ContainerManagerServicer_to_server(
        ContainerManagerHandler(), server)
    server.add_insecure_port('[::]:8666')
    server.start()
    print("Starting python server...")
    server.wait_for_termination()
