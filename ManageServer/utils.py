import docker
import os
import tarfile
import re
import requests

DOCKERCLIENT = docker.from_env()
CONTAINER_ATTRS = [['Id'], ['Created'], ['State'], ['Image'], ['Name']]
IMAGE_ATTRS = [['Id'], ['RepoTags'], ['Created'], ['Size'], ['Author']]




class ContainerUtils:
    @staticmethod
    def PruneContainers():
        DOCKERCLIENT.containers.prune()

    @staticmethod
    def ListContainers():
        ret = []
        List = DOCKERCLIENT.containers.list()
        for container in List:
            ret.append(ContainerUtils.GetContainer(container.id))
        return ret

    @staticmethod
    def GetContainer(container_id):
        ret = {}
        temp = DOCKERCLIENT.containers.get(container_id)
        for attr in CONTAINER_ATTRS:
            it = iter(attr)
            key = None
            value = temp.attrs
            while True:
                try:
                    key = next(it)
                    value = value[key]
                except StopIteration:
                    break
            ret[key] = value
        return ret
    @staticmethod
    def CreateContainer(image_id, mount_path, container_name):
        if not os.path.exists(mount_path):
            os.makedirs(mount_path)
        
        execCommand = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] && ([ -x /usr/bin/script ] && /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) || exec /bin/sh']
        execOptions = {
            "tty": True,
            "stdin": True
        }
        container = DOCKERCLIENT.containers.create(
            image = image_id,
            command = execCommand,
            tty = True,
            stdin_open = True,
            name = container_name,
            mounts=[
                docker.types.Mount(
                    target = '/mnt',
                    source = mount_path,
                    type = 'bind'
                )
            ]
        )
        return container.id
    @staticmethod
    def StartContainer(container_id):
        container = DOCKERCLIENT.containers.get(container_id)
        container.start()
    @staticmethod
    def StopContainer(container_id):
        container = DOCKERCLIENT.containers.get(container_id)
        container.stop()
    @staticmethod
    def RemoveContainer(container_id, force = False):
        container = DOCKERCLIENT.containers.get(container_id)
        container.remove(force = force)
    @staticmethod
    def RestartContainer(container_id):
        container = DOCKERCLIENT.containers.get(container_id)
        container.restart()
    
    @staticmethod
    def CommitContainer(container_id, repository, tag=None, author=None):
        container = DOCKERCLIENT.containers.get(container_id)
        container.commit(\
            repository=repository,
            tag = tag,
            author = author
        )
    
    @staticmethod 
    def GetArchive(container_id, path, chunk_size=2097152):
        container = DOCKERCLIENT.containers.get(container_id)
        return container.get_archive(path, chunk_size=chunk_size)

    @staticmethod 
    def PutArchive(container_id, path, data):
        container = DOCKERCLIENT.containers.get(container_id)
        return container.put_archive(path, data)

    @staticmethod 
    def ExecCommand(container_id, exec_cmd):
        container = DOCKERCLIENT.containers.get(container_id)
        exit_code, output = container.exec_run(
            cmd=exec_cmd
        )
        output = str(output, encoding='utf-8').strip()
        return exit_code, output

    # @staticmethod
    # def GetFileStat(container_id, path):
    #     container = DOCKERCLIENT.containers.get(container_id)
    #     exit_code, output = container.exec_run(
    #         cmd=["stat","-c","%Y",path]
    #     )
    #     modify_time = str(output, encoding='utf-8')
    #     return exit_code, modify_time


class ImageUtils:
    @staticmethod
    def PruneImages():
        filters = {'dangling':True}
        DOCKERCLIENT.images.prune(filters=filters)


    @staticmethod
    def ListImages():
        ret = []
        List = DOCKERCLIENT.images.list()
        for container in List:
            ret.append(ImageUtils.GetImage(container.id))
        return ret

    @staticmethod
    def PullImage(repository, tag = None, auth_config=None):
        DOCKERCLIENT.images.pull(repository= repository, tag= tag, auth_config= auth_config)

    @staticmethod
    def BuildImageByPath(path, tag):
        DOCKERCLIENT.images.build(path=path, tag=tag , quiet=True)

    @staticmethod
    def BuildImageByFile(fileobj, tag):
        DOCKERCLIENT.images.build(fileobj=fileobj, tag=tag , quiet=True)

    @staticmethod
    def LoadImage(data):
        return DOCKERCLIENT.images.load(data)

    @staticmethod
    def GetImage(image_id):
        ret = {}
        temp = DOCKERCLIENT.images.get(image_id)
        # for x in temp.attrs:
        #     print(x)
        for attr in IMAGE_ATTRS:
            it = iter(attr)
            key = None
            value = temp.attrs
            while True:
                try:
                    key = next(it)
                    value = value[key]
                except StopIteration:
                    break
            # if type(value) is type([]):
            #     value = value[0]
            ret[key] = value
        return ret

    @staticmethod
    def RemoveImage(image_id, force = False):
        DOCKERCLIENT.images.remove(image_id, force=force)

# def tarFile(output_filename, source_dir):
#     with tarfile.open(output_filename, "w:gz") as tar:
#         tar.add(source_dir, arcname=os.path.basename(source_dir)

def ExportFile(username, url):
    path = "/workplace/{username}/mount.tar".format(username=username)
    url = 'http://111.230.172.240:7777/upload'
    files = {'file':open('test.cpp','r')}
    response = requests.post(url,files = files)

def ImportFile(username, url):
    # path = 'get.cpp'
    path = "/workplace/{username}/mount.tar".format(username=username)
    response = requests.get(url)
    file = open(path,"w")
    file.write(response.text)
    file.close()

if __name__ == '__main__':
    container = DOCKERCLIENT.containers.get('container1')
    print(container.attrs['State'])