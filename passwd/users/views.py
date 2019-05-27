import grp
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
        vals = line.split(':')
        del vals[1]
        vals[-1] = vals[-1].replace('\n', '')

        user_entry = {}
        if len(vals) < 6:
            keys.remove('comment')
            user_entry = zip(keys, vals)
            user_entry['comment'] = ""
            keys.insert('comment', 3)
        else:
            user_entry = zip(keys, vals)
        resp.append(user_entry)
    return resp


def _parse_grp_info(group_info):
    grp_keys = ['name', 'gid', 'members']
    grp_vals = list(group_info)
    del grp_vals[1]

    return dict(zip(grp_keys, grp_vals))


def _get_users():
    resp = []
    for user_entry in _parse_passwd():
        resp.append(dict(user_entry))
    return resp


def _get_by_uid():
    resp = {}
    for user_entry in _parse_passwd():
        temp = dict(user_entry)
        uid = temp['uid']
        del temp['uid']

        user_entry = {uid: temp}
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
            resp = _get_by_uid().get(uid_val)
            resp['uid'] = uid_val
            return JsonResponse(resp)
    return HttpResponse(status=404)


def group_uid(request):
    if request.method == "GET":
        uid_val = request.path.split('/')[-2]
        if _get_by_uid().get(uid_val):
            user_val = _get_by_uid()[uid_val]
            grp_info = grp.getgrgid(user_val['gid'])
            return JsonResponse(_parse_grp_info(grp_info))
    return HttpResponse(status=404)
