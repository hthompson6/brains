from itertools import zip_longest as zip

from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

def index(request):
    if request.method == "GET":
        f = open('/etc/passwd', 'r')
        keys = ['name', 'uid', 'gid', 'comment', 'home', 'shell']

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
            resp.append(dict(user_entry))
        return JsonResponse(resp, safe=False)
    return HttpResponse("Hello, world. ou're at the polls index.")
