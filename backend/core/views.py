from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import Job, Interest
from django.forms.utils import ErrorList

User = get_user_model()

def job_list(request):
    jobs = Job.objects.order_by('id')[:50]

    if not request.user.is_authenticated:
        return redirect('authorization')
    else:
        return render(request, 'core/index.html', {'jobs': jobs})

def job_detail(request, job_id):
    job = Job.objects.get(pk=job_id)
    return render(request, 'core/job_detail.html', {'job': job})

def auth_view(request):
    if request.method == 'GET':
        form_type = request.GET.get('form_type', 'login')
        register_form = CustomUserCreationForm()
        login_form = CustomLoginForm()
        return render(request, 'core/register.html', {
            'register_form': register_form,
            'login_form': login_form,
            'form_type': form_type,
        })

    form_type = request.POST.get('form_type', 'register')

    register_form = CustomUserCreationForm()
    login_form = CustomLoginForm(request, data=request.POST)

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

            return render(request, 'core/register.html', {
                'register_form': CustomUserCreationForm(),
                'login_form': CustomLoginForm(),
                'form_type': 'login',
                'email_sent': True
            })

    elif form_type == 'login':
        login_form = CustomLoginForm(request, data=request.POST)

        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)

            if not hasattr(user, 'interests') or user.interests.count() == 0:
                return redirect('interests')

        return redirect('home')

    return render(request, 'core/register.html', {
        "register_form": register_form,
        "login_form": login_form,
        "form_type": form_type,
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
        login(request, user)  # 🔥 log the user in
        return redirect('interests')  # 🔥 use redirect, not render
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

    return render(request, 'core/interests.html', {
        'name': user.name,
        'interests': interests,
        'error': error
    })


def account_view(request):
    if not request.user.is_authenticated:
        return redirect('authorization')

    user = request.user
    interests = user.interests.all() if hasattr(user, 'interests') else None
    return render(request, 'core/account.html', {
        'user': user,
        'interests': interests,
    })

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('authorization')