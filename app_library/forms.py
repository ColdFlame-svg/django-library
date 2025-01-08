from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Staff, Book, Transaction, Admin

class CreateAccountForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    terms_accepted = forms.BooleanField(required=True)

    class Meta:
        model = User  # Your custom User model
        fields = ['student_id', 'first_name', 'middle_name', 'last_name', 'suffix', 'email', 'password', 'confirm_password', 'terms_accepted']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        
        # Check if terms are accepted
        if not cleaned_data.get("terms_accepted"):
            raise ValidationError("You must accept the terms and conditions.")
        
        # Hash the password before saving
        cleaned_data['password'] = make_password(password)  # Hash the password
        
        return cleaned_data


class AddStaffForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Staff
        fields = ['staff_id', 'first_name', 'last_name', 'email', 'password', 'is_active']  # Exclude 'user'

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.password = make_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            instance.save()
        return instance

    
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['isbn', 'title', 'author', 'published_date', 'description', 'image', 'status']  # Add 'status' to the fields
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(choices=Book.STATUS_CHOICES)  # Use Select widget for status dropdown
        }
    
    # Set a default value for the 'status' field
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        # Set the initial value of 'status' to 'available' if not provided
        self.fields['status'].initial = 'available'

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    re_enter_password = forms.CharField(widget=forms.PasswordInput, label="Re-enter New Password")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        re_enter_password = cleaned_data.get("re_enter_password")

        if new_password and new_password != re_enter_password:
            raise forms.ValidationError("New passwords do not match.")
        return cleaned_data

    def save(self):
        # Save the new password to the user
        new_password = self.cleaned_data.get("new_password")
        self.user.set_password(new_password)
        self.user.save()
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'student_id', 'title', 'borrow_date', 'return_date']

    # Custom widget for student_id (foreign key to User model)
    student_id = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=False, is_superuser=False, is_admin=False), empty_label="Select Student")

    # Custom widget for title (foreign key to Book model)
    title = forms.ModelChoiceField(queryset=Book.objects.all(), empty_label="Select Book")

    # Custom widget for return_date (date picker)
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),  # This makes it a date picker
        required=False,  # Optional, depending on your requirements
    )

class StaffPasswordChangeForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter current password'}),
        label="Current Password",
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}),
        label="New Password",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label="Confirm New Password",
    )

    class Meta:
        model = User  # Change this to User model
        fields = []  # No model fields directly tied to this form

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('instance', None)  # This should be a User instance
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        # Validate current password using the User model
        if not self.user or not self.user.check_password(current_password):
            self.add_error('current_password', 'The current password is incorrect.')

        # Validate new password confirmation
        if new_password != confirm_password:
            self.add_error('confirm_password', 'The new passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        # Update the User model password
        self.user.set_password(self.cleaned_data['new_password'])  # Hash and set the new password
        if commit:
            self.user.save()
        return self.user