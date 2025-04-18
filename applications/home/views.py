from django.shortcuts import render

def vista_home(request):
    return render(request, 'home/index.html')

