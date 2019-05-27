import grp
from itertools import zip_longest as zip

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

keys = ['name', 'gid', 'members'] 


def _parse_grp():
    f = open('/etc/group', 'r')

    resp = []
    for line in f:
        vals = line.split(':')
        del vals[1]
        vals[-1] = vals[-1].replace('\n', '')

        group_entry = {}
        group_entry = zip(keys, vals)
        resp.append(group_entry)
    return resp


def _transform_mems(group_entry):
    group_entry['members'] = group_entry['members'].split(',')
    return group_entry


def _get_groups():
    resp = []
    for group_entry in _parse_grp():
        temp = _transform_mems(dict(group_entry))
        resp.append(dict(temp))
    return resp


def _get_by_gid():
    resp = {}
    for group_entry in _parse_grp():
        temp = _transform_mems(dict(group_entry))
        uid = temp['gid']
        del temp['gid']

        user_entry = {uid: temp}
        resp.update(user_entry)
    return resp


def index(request):
    if request.method == "GET":
        return JsonResponse(_get_groups(), safe=False)
    return HttpResponse(status=404)


def query(request):
    if request.method == "GET":
        group_lst = _get_groups()
        if len(request.GET) != 0:
            for k in request.GET.keys():
                if k not in ['name', 'gid', 'member']:
                    return HttpResponse(status=404)
                else:
                    cnt = 0
                    while cnt < len(group_lst):
                        if k == 'member':
                            for member in request.GET.getlist(k):
                                if member not in group_lst[cnt]['members']:
                                    del group_lst[cnt]
                                    cnt -= 1
                                    break
                        elif group_lst[cnt][k] != request.GET[k]:
                            del group_lst[cnt]
                            cnt -= 1 
                        cnt += 1 
        return JsonResponse(group_lst, safe=False)
    return HttpResponse(status=404)


def gid(request):
    if request.method == "GET":
        gid_val = request.path.split('/')[-1]
        if _get_by_gid().get(gid_val):
            resp = _get_by_gid().get(gid_val)
            resp['gid'] = gid_val
            return JsonResponse(resp)
    return HttpResponse(status=404)
