from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from store.models.customer.customer import Customer


class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CustomerLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
