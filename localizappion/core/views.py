from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse('This should list all available projects')

