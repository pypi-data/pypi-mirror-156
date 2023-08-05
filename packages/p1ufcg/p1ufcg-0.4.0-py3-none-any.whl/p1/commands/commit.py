from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import io
import os
import sys

import p1
from p1.utils import data2json, _assert, cprint
from p1.colors import *
from p1.jsonfile import JsonFile

def touch_option(args):
    touch = False
    for i, a in enumerate(args):
        if a in ['-t', '--touch']:
            args.pop(i)
            touch = True

    return touch


def main():
    _assert(len(sys.argv) in [3, 4], 'Usage: p1 commit [--support-file|-s] [--touch|-t] <filename>')
    _assert(os.path.exists('.p1/assignment.json'), 'No p1 assignment found')
    touch = touch_option(sys.argv)
    filetype = 'support' if sys.argv[2] in ['--support-file', '-s'] else 'answer'
    filename = sys.argv[3 if filetype == 'support' else 2]
    assignment_id = JsonFile('.p1/assignment.json')['iid']
    site = p1.get_site('_DEFAULT')
    commit(filename, filetype, assignment_id, site, touch)


def read_mode(filename):
    return "rw"


def read_content(filename):
    with io.open(filename, encoding='utf-8') as f:
        content = f.read()

    return content


def commit(filename, filetype, key, site, touch):
    content = read_content(filename)
    checksum = hashlib.sha1(content.encode('utf-8')).hexdigest()
    data = {
        "files": [{
                "name": filename,
                "content": content,
                "mode": read_mode(filename),
                "category": "public",
                "type": filetype,
                "hash": checksum
            }],
        "hash": checksum,
    }
    if touch: 
        data["touch"] = True

    response = site.send_answer(data, key)
    if response.ok:
        cprint(LGREEN, 'Commit feito com sucesso')
        try:
            for msg in response.json()['messages']:
                cprint(YELLOW, f"- {msg}")
        except:
            pass

    elif response.status_code == 401:
        cprint(LRED, 'Você precisa fazer o login' % response.status_code)
        cprint(LRED, 'Execute: p1 login')
    else:
        ERRORS = ['HTTPClientError']
        messages = [m for m in response.json()['messages'] if m not in ERRORS]
        cprint(LRED, 'O servidor não aceitou a resposta (%s)' % response.status_code)
        try:
            for msg in messages:
                cprint(YELLOW, f"- {msg}")
        except:
            pass
