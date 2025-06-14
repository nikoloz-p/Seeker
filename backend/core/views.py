from django.shortcuts import render
from .models import Job
from django.db.models import Q


def job_list(request):

    jobs = Job.objects.order_by('id')[:50]
    return render(request, 'core/index.html', {'jobs': jobs})

def job_detail(request, job_id):

    job = Job.objects.get(pk=job_id)
    return render(request, 'core/job_detail.html', {'job': job})