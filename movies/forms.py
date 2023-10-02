from django import forms


class ParticipantInfoForm(forms.Form):
    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    age = forms.IntegerField(min_value=18, max_value=1000, required=True)
    country = forms.CharField(max_length=100, required=True)
