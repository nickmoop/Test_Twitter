from django import forms


class Login(forms.Form):
    email = forms.CharField(label='email', max_length=140)
    password = forms.CharField(label='password', max_length=140)


class Tweet(forms.Form):
    message = forms.CharField(label='message', max_length=140)


class Search(forms.Form):
    user = forms.CharField(label='user', max_length=140)
    message = forms.CharField(label='message', max_length=140)
