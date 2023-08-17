from django import forms
from .models import Product
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','description','price','product_image']

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label=' Confirm password',widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username','email','first_name' ]

    def check_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError('Password fields do not match')
        
        return self.cleaned_data['password2']

# class UserRegistrationForm(forms.ModelForm):
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name']

#     def clean_password2(self):
#         # Check if passwords match
#         password = self.cleaned_data.get('password')
#         password2 = self.cleaned_data.get('password2')
#         if password and password2 and password != password2:
#             raise forms.ValidationError('Passwords do not match.')
#         return password2
