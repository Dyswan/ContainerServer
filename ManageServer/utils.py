import docker
import os 
DOCKERCLIENT = docker.from_env()
CONTAINER_ATTRS = [['Id'], ['Created'], ['State', 'Status'], ['Image'], ['Name']]
IMAGE_ATTRS = [['Id'], ['RepoTags'], ['Created'], ['Size'], ['Author']]

class ContainerUtils:
    @staticmethod
    def PruneContainers():
        DOCKERCLIENT.containers.prune()

    @staticmethod
    def ListContainers():
        ret = {}
        List = DOCKERCLIENT.containers.list()
        for container in List:
            ret[container.id] = ContainerUtils.GetContainer(container.id)
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
                    target = '/workplace',
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
    def GetArchive(container_id, path, chunk_size=2097152):
        container = DOCKERCLIENT.containers.get(container_id)
        return container.get_archive(path, chunk_size=chunk_size)

    @staticmethod 
    def ExecCommand(container_id, exec_cmd):
        container = DOCKERCLIENT.containers.get(container_id)
        exit_code, output = container.exec_run(
            cmd=exec_cmd
        )
        output = str(output, encoding='utf-8')
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
        ret = {}
        List = DOCKERCLIENT.images.list()
        for container in List:
            ret[container.id] = ImageUtils.GetImage(container.id)
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
        DOCKERCLIENT.images.load(data)

    @staticmethod
    def GetImage(image_id):
    # image_id 可以是id也可以是name
        ret = {}
        temp = DOCKERCLIENT.images.get(image_id)
        for x in temp.attrs:
            print(x)
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


if __name__ == '__main__':
    # print(GetContainer('test'))
    # print(GetImage('judger:v1.0'))
    # container = DOCKERCLIENT.containers.get('test')
    # exit_code, output = container.exec_run(
    #     cmd=["stat","-c","%Y","/etc/apt/sources.list"]
    # )
    # print(str(output, encoding='utf-8'),end="")
    ContainerUtils.GetFileStat('container1', '/etc/apt/sour')
