from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    username = None
    email = forms.EmailField(required=True, label='ელ-ფოსტა')
    name = forms.CharField(required=True, label='სახელი და გვარი')
    password1 = forms.CharField(required=True, label='პაროლი', widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, label='გაიმეორე პაროლი', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs.update({
            'placeholder': 'სახელი და გვარი'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'ელ-ფოსტა'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'პაროლი'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'გაიმეორე პაროლი'
        })
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'auth_form-input'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'ამ ელ-ფოსტით უკვე დარეგისტრირებულია მომხმარებელი.')

        return email

    def clean_password1(self):
        symbols = '~!@#$%^&*()_-+={[}]|\\:;<,>.?/'
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 8:
            self.add_error('password1', 'პაროლი უნდა შეიცავდეს მინიმუმ 8 სიმბოლოს.')
        if password1.isdigit():
            self.add_error('password1', 'პაროლი არ უნდა შეიცავდეს მხოლოდ ციფრებს.')
        if password1.isalpha():
            self.add_error('password1', 'პაროლი არ უნდა შეიცავდეს მხოლოდ ასოებს.')
        if not any(char in symbols for char in password1):
            raise forms.ValidationError(
                'პაროლი უნდა შეიცავდეს სპეციალურ სიმბოლოს. მაგალითად: ~!@#$%^&*()_-+={[}]|\\:;<,>.?/')

        return password1
