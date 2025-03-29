from django import forms
from .models import User



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Password field with hidden input

    class Meta:
        model = User
        fields = ['name', 'phone_number', 'password']


from django import forms


from django import forms
from django.core.validators import RegexValidator
from .models import Transaction

class SendMoneyForm(forms.Form):
    sender_phone = forms.CharField(max_length=15, required=True)
    receiver_phone = forms.CharField(max_length=15, required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, required=True)

from django import forms

class ChatForm(forms.Form):
    user_input = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ask me a question...'}), label="")


from django import forms
from .models import User

class BillSplitForm(forms.Form):
    bill_amount = forms.DecimalField(max_digits=10, decimal_places=2)
    participants_phones = forms.CharField(widget=forms.Textarea, help_text="Enter phone numbers of users (separate by comma)")
    merchant_phone = forms.CharField(max_length=15, help_text="Enter merchant phone number")
    
    def clean_participants_phones(self):
        # Clean participants' phone numbers and ensure all are registered users
        phone_numbers = self.cleaned_data['participants_phones'].split(',')
        valid_phones = []
        for phone in phone_numbers:
            phone = phone.strip()  # Remove leading/trailing whitespaces
            if not User.objects.filter(phone_number=phone).exists():
                raise forms.ValidationError(f"User with phone number {phone} is not registered.")
            valid_phones.append(phone)
        return valid_phones
    
    from django import forms

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=15)