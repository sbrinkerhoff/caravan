
import sys

import requests
import json
import argparse

server = 'http://localhost:8888'


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", default='http://localhost:8888')
    parser.add_argument("--user", default='sbrinkerhoff@northernpower.com')
    parser.add_argument("--password", default='stanspassword')
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--target")
    parser.add_argument("--task")
    args = parser.parse_args()

    if args.verbose:
       print "verbosity turned on"

    if args.task:
        print "new task request"

        a = dict()

        a['user'] = args.user
        a['password'] = args.password
        a['target'] = args.target
        a['task'] = args.task

        r = requests.post(server + '/api/1/job/new', data=a)
        print r.text

if __name__ == "__main__":
    main()
