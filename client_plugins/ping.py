
import subprocess
import traceback
import json

from caravan.plugin import PluginResponse, CaravanPlugin

def activate():
    return (PingPlugin(),)

class PingPlugin(CaravanPlugin):
    __name__ = "Ping Plugin"
    __version__ = "1.0.0"
    __tasks__ = ('ping',)

    def execute_task(self, task):

        try:
            p = subprocess.Popen('ping %s' % task['args'], shell=True, stdout=subprocess.PIPE)
            ret = {'data': p.stdout.readlines()}
            return PluginResponse('complete',json.dumps(ret))

        except:
            print "Excepted"
            t=traceback.format_exc()
            return PluginResponse('error', json.dumps({'status':'error','data':t}))
