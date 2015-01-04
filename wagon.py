import pkgutil
import sys
import logging
import json
import time
import socket


import wmi

import requests

print wmi.WMI().Win32_Processor()[0]

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

server = 'http://fleet.vtwireless.com:8888'

__VERSION__ = '0.0.1'

a = dict()
a['user'] = socket.gethostname()
a['passwd'] = 'asdjfjfasklfjasf'
a['version'] = __VERSION__
a['apiver'] = 1

def fetch_task(server, task):
    b = a
    b['task_id'] = task
    r = requests.get(server + '/api/1/client/task/fetch', data=b)
    print "## %s" % r.text
    return json.loads(r.text)

def accept_task(server, task):
    b = a
    b['task_id'] = task
    r = requests.get(server + '/api/1/client/task/accept', data=b)
    print r.text


def respond_task(server, response, task, result):
    b = a
    b['task_id'] = task
    b['result'] = result

    r = requests.post(server + '/api/1/client/task/%s' % response, data=b)
    print r.text

def decline_task(server, task, result):
    respond_task(server, 'decline', task, result)

def complete_task(server, task, result):
    respond_task(server, 'complete', task, result)

def error_task(server, task, result):
    respond_task(server, 'error', task, result)



def load_all_modules_from_dir(dirname):
    plugins = list()

    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(package_name
                        ).load_module(full_package_name)
            try:
                p = module.activate()
                print p
                for plugin in p:

                    #print "adding %s" % plugin
                    plugins.append(plugin)
            except AttributeError, ex:
                print 'Failed to activate plugins from %s' % full_package_name
                continue

    return plugins

plugins = load_all_modules_from_dir('client_plugins')



def main():

    print "Plugins Loaded:"
    for x in plugins:
        print "## %s loaded supporting tasks:" % x.name()
        print ",".join(x.tasks_supported())
        print ""

    while True:
        logger.info('Connecting to server %s' % server)

        try:
            r = requests.get(server + '/api/1/client/task', data=a, timeout=60)

            print r.text
            if r.text:
                x = json.loads(r.text)
                print x

                task = fetch_task(server, x['task_id'])

                print "Received task: %s" % task['task']

                for p in plugins:
                    if task['task'] in p.tasks_supported():
                        response = p.execute_task(task)

                        if response.status == "complete":
                            complete_task(server, x['task_id'], response.response)
                        if response.status == "error":
                            error_task(server, x['task_id'], response.response)

                        continue

                decline_task(server, x['task_id'], json.dumps({'data': 'no plugin supporting task request found'}))

        except requests.exceptions.ConnectionError, ex:
            logger.error('Cound not connect to server %s' % server)
            time.sleep(10)

        except requests.exceptions.ReadTimeout, ex:
            pass # this is ok



        continue


if __name__ == "__main__":
    main()