from django.forms.utils import ErrorList
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from .forms import CustomUserCreationForm, CustomLoginForm, ProfileUpdateForm
from .models import Job, Interest, HrGe, JobsGe, MyJobsGe
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from urllib.parse import urlparse
import random


User = get_user_model()

def job_list(request):
    hr_jobs = list(HrGe.objects.all())
    jobs_ge = list(JobsGe.objects.all())
    myjobs_ge = list(MyJobsGe.objects.all())

    icon_map = {
        "hr.ge": "images/src_website_logos/hrge_logo.svg",
        "jobs.ge": "images/src_website_logos/jobsge_logo.png",
        "myjobs.ge": "images/src_website_logos/myjobsge_logo.svg",
    }

    all_jobs = hr_jobs + jobs_ge + myjobs_ge
    random.shuffle(all_jobs)

    for job in all_jobs:
        domain = urlparse(job.position_url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        source_site = domain
        source_icon = icon_map.get(source_site, "images/src_website_logos/default_logo.svg")

        setattr(job, 'source_site', source_site)
        setattr(job, 'source_icon', source_icon)

    random_jobs = all_jobs[:50]

    return render(request, 'core/index.html', {'jobs': random_jobs})


def job_detail(request, job_id):
    job = Job.objects.get(pk=job_id)
    return render(request, 'core/job_detail.html', {'job': job})

def auth_view(request):
    form_type = request.GET.get('form_type', 'login') if request.method == 'GET' else request.POST.get('form_type', 'register')
    user = request.user
    register_form = CustomUserCreationForm()
    login_form = CustomLoginForm()

    if request.method == 'POST':
        
        if form_type == "register":
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.username = register_form.cleaned_data['email']
                user.email = register_form.cleaned_data['email']
                user.first_name = register_form.cleaned_data['name']
                user.set_password(register_form.cleaned_data['password1'])
                user.is_active = False
                user.save()
                send_verification_email(request, user)
                
                messages.success(request, "გთხოვთ გადაამოწმოთ თქვენი ელ.ფოსტა და დაადასტუროთ ანგარიში.")
                return redirect('/authorization?form_type=login')
            else:
                request.session['register_errors'] = register_form.errors.get_json_data()

        elif form_type == 'login':
            login_form = CustomLoginForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                if not hasattr(user, 'interests') or user.interests.count() == 0:
                    return redirect('interests')
                return redirect('home')
            else:
                request.session['login_errors'] = login_form.errors.get_json_data()

        return redirect(f'/authorization?form_type={form_type}')

    if form_type == "register":
        register_form = CustomUserCreationForm()
        if 'register_errors' in request.session:
            errors = request.session.pop('register_errors')
            for field, field_errors in errors.items():
                register_form.errors.setdefault(field, ErrorList()).extend([e['message'] for e in field_errors])
    else:
        login_form = CustomLoginForm()
        if 'login_errors' in request.session:
            errors = request.session.pop('login_errors')
            for field, field_errors in errors.items():
                login_form.errors.setdefault(field, ErrorList()).extend([e['message'] for e in field_errors])

    if user.is_authenticated:
        if not hasattr(user, 'interests') or user.interests.count() == 0:
            return redirect('interests')
        else:
            return redirect('home')
    else:
        return render(request, 'core/register.html', {
            'register_form': register_form,
            'login_form': login_form,
            'form_type': form_type,
        })

def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    link = reverse('activate-account', kwargs={'uidb64': uid, 'token': token})
    activate_url = f'http://{domain}{link}'

    message = render_to_string('core/registration/verify_email.html', {
        'user': user,
        'activate_url': activate_url,
    })

    send_mail(
        'ანგარიშის აქტივაცია',
        message,
        None,
        [user.email],
        fail_silently=False,
    )


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  
        return redirect('interests')
    else:
        return render(request, 'core/registration/verify_failed.html')


def interests_view(request):

    if not request.user.is_authenticated:
        return redirect('authorization')
    
    if hasattr(request.user, 'interests') and request.user.interests.exists():
        return redirect('account')

    if request.method == 'POST':
        selected = request.POST.getlist('interests')
        if len(selected) == 3:
            request.user.interests.set(selected)
            return redirect('home')
        else:
            error = "გთხოვთ აირჩიოთ ზუსტად 3 ინტერესის სფერო."
    else:
        error = None

    interests = Interest.objects.all()
    user = request.user
    first_name = request.user.name.split(' ')[0]

    return render(request, 'core/interests.html', {
        'name': first_name,
        'interests': interests,
        'error': error
    })


def account_view(request):
    if not request.user.is_authenticated:
        return redirect('authorization')

    user = request.user
    interests = user.interests.all() if hasattr(user, 'interests') else None

    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('account')

    return render(request, 'core/account.html', {
        'user': user,
        'interests': interests,
        'form': form,
    })



def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('authorization')