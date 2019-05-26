from collections import OrderedDict
from itertools import zip_longest as zip

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


def get_keys():
    '''
    These keys are needed in multiple places. Occasionally they are altered,
    this could cause unintended side effects so they've been turned into a fuction
    '''
    return ['name', 'uid', 'gid', 'comment', 'home', 'shell']


def _parse_passwd():
    f = open('/etc/passwd', 'r')
    keys = get_keys()

    resp = []
    for line in f:
        line_arr = line.split(':')
        del line_arr[1]
        line_arr[-1] = line_arr[-1].replace('\n', '')

        user_entry = {}
        if len(line_arr) < 6:
            keys.remove('comment')
            user_entry = zip(keys, line_arr)
            user_entry['comment'] = ""
            keys.insert('comment', 3)
        else:
            user_entry = zip(keys, line_arr)
        resp.append(user_entry)
    return resp


def _get_users():
    resp = []
    for user_entry in _parse_passwd():
        resp.append(dict(user_entry))
    return resp


def _get_by_uid():
    resp = {}
    for user_entry in _parse_passwd():
        temp_dict = dict(user_entry)
        uid = temp_dict['uid']
        del temp_dict['uid']

        user_entry = {uid: temp_dict}
        resp.update(user_entry)
    return resp


def index(request):
    if request.method == "GET":
        return JsonResponse(_get_users(), safe=False)
    return HttpResponse(status=404)


def query(request):
    if request.method == "GET":
        user_lst = _get_users()
        if len(request.GET) != 0:
            for k in request.GET.keys():
                if k not in get_keys():
                    return HttpResponse(status=404)
                cnt = 0
                while cnt < len(user_lst):
                    if user_lst[cnt][k] != request.GET[k]:
                        del user_lst[cnt]
                        cnt -= 1 
                    cnt += 1 

        return JsonResponse(user_lst, safe=False)
    return HttpResponse(status=404)


def uid(request):
    if request.method == "GET":
        uid_val = request.path.split('/')[-1]
        if _get_by_uid().get(uid_val):
            return JsonResponse(_get_by_uid().get(uid_val))
    return HttpResponse(status=404)
