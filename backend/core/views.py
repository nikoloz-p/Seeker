from django.shortcuts import render, redirect
from .models import Job
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .forms import CustomUserCreationForm

# jobs views
def job_list(request):
    jobs = Job.objects.order_by('id')[:50]
    return render(request, 'core/index.html', {'jobs': jobs})

def job_detail(request, job_id):
    job = Job.objects.get(pk=job_id)
    return render(request, 'core/job_detail.html', {'job': job})


# registration views
User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.email = form.cleaned_data['email']
            user.name = form.cleaned_data['name']
            user.set_password(form.cleaned_data['password1'])
            user.is_active = False
            user.save()

            send_verification_email(request, user)
            return render(request, 'core/registration/verify_email_sent.html')

        else:
            print("Form is not valid:")
            print(form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, 'core/register.html', {'form': form})

# account activation views
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
        return render(request, 'core/registration/verify_success.html')
    else:
        return render(request, 'core/registration/verify_failed.html')