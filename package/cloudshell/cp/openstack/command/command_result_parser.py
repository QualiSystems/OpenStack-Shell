import jsonpickle

class OpenStackShellCommandResultParser(object):
    def __init__(self):
        pass

    @staticmethod
    def set_command_result(deploy_data, unpicklable=False):
        return jsonpickle.encode(deploy_data, unpicklable=unpicklable)

