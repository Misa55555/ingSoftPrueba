from django.shortcuts import render

def vista_analisis(request):
    return render(request, 'analisis/analisis.html')

