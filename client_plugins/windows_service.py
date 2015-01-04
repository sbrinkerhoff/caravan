
import subprocess
import json

from caravan.plugin import PluginResponse, CaravanPlugin

def activate():
    return (ServicePlugin(),)

class ServicePlugin(CaravanPlugin):
    __name__ = "StartServicePlugin"
    __version__ = "1.0.0"
    __tasks__ = ('service_stop', 'service_start','service_query')
    def execute_task(self, task):

        if task['task'] == 'service_stop':
            p = subprocess.Popen('sc stop %s' % task['args'], shell=True, stdout=subprocess.PIPE)
            ret = {'data': p.stdout.readlines()}
            return PluginResponse('complete', json.dumps(ret))

        if task['task'] == 'service_start':
            p = subprocess.Popen('sc start %s' % task['args'], shell=True, stdout=subprocess.PIPE)
            ret = {'data': p.stdout.readlines()}
            return PluginResponse('complete', json.dumps(ret))

        if task['task'] == 'service_query':
            p = subprocess.Popen('sc query %s' % task['args'], shell=True, stdout=subprocess.PIPE)
            ret = {'data': p.stdout.readlines()}
            return PluginResponse('complete', json.dumps(ret))


