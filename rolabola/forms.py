from django import forms

class SearchForm(forms.Form):
    name = forms.CharField()
    qtype = forms.CharField(widget=forms.HiddenInput(), initial="User")
