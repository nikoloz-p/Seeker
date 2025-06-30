from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    username = None
    email = forms.EmailField(required=True, label='ელ-ფოსტა')
    name = forms.CharField(required=True, label='სახელი და გვარი')
    password1 = forms.CharField(required=True, label='პაროლი', widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, label='გაიმეორე პაროლი', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({'placeholder': 'სახელი და გვარი'})
        self.fields['email'].widget.attrs.update({'placeholder': 'ელ-ფოსტა'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'პაროლი'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'გაიმეორე პაროლი'})

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'auth_form-input'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('ამ ელ-ფოსტით უკვე დარეგისტრირებულია მომხმარებელი.')
        return email

    def clean_password1(self):
        symbols = '~!@#$%^&*()_-+={[}]|\\:;<,>.?/'
        password1 = self.cleaned_data.get('password1')

        if password1:
            if len(password1) < 8:
                raise forms.ValidationError('პაროლი უნდა შეიცავდეს მინიმუმ 8 სიმბოლოს.')
            if password1.isdigit():
                raise forms.ValidationError('პაროლი არ უნდა შეიცავდეს მხოლოდ ციფრებს.')
            if password1.isalpha():
                raise forms.ValidationError('პაროლი არ უნდა შეიცავდეს მხოლოდ ასოებს.')
            if not any(char in symbols for char in password1):
                raise forms.ValidationError(
                    'პაროლი უნდა შეიცავდეს სპეციალურ სიმბოლოს. მაგალითად: ~!@#$%^&*()_-+={[}]|\\:;<,>.?/')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("პაროლები არ ემთხვევა.")
        return password2



class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='ელ-ფოსტა', widget=forms.EmailInput(attrs={
        'placeholder': 'ელ-ფოსტა',
        'class': 'auth_form-input',
    }))
    password = forms.CharField(label='პაროლი', widget=forms.PasswordInput(attrs={
        'placeholder': 'პაროლი',
        'class': 'auth_form-input',
    }))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                raise self.get_invalid_login_error()

            if not user.check_password(password):
                raise self.get_invalid_login_error()

            if not user.is_active:
                raise forms.ValidationError(
                    "თქვენი ანგარიში არ არის აქტიური. გთხოვთ, დაადასტუროთ ელ-ფოსტა.",
                    code='inactive',
                )

            self.confirm_login_allowed(user)
            self.user_cache = user

        return self.cleaned_data

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            "ელ-ფოსტა ან პაროლი არასწორია.",
            code='invalid_login',
        )

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']