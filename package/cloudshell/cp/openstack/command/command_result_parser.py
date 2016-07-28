import jsonpickle

class OpenStackShellCommandResultParser(object):
    def __init__(self):
        pass

    @staticmethod
    def set_command_result(deploy_data, picklable=False):
        return jsonpickle.encode(deploy_data, picklable=picklable)

