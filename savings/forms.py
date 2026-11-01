from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Contribution, AjoPayout

User = get_user_model()

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "phone", "email"]
        widgets = {"full_name": forms.TextInput(attrs={"placeholder": "Enter member's full name"}), "phone": forms.TextInput(attrs={"placeholder": "e.g. 08012345678"}), "email": forms.EmailInput(attrs={"placeholder": "name@example.com"})}

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ["member", "amount", "contribution_date"]
        widgets = {"member": forms.Select(), "amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01", "placeholder": "e.g. 5000"}), "contribution_date": forms.DateInput(attrs={"type": "date"})}

class MemberRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=25)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "full_name", "email", "phone")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Member.objects.create(user=user, full_name=self.cleaned_data["full_name"], email=self.cleaned_data["email"], phone=self.cleaned_data["phone"])
        return user


class AjoPayoutForm(forms.ModelForm):
    class Meta:
        model = AjoPayout
        fields = ["round_number", "recipient", "scheduled_date", "amount", "notes"]
        widgets = {
            "round_number": forms.NumberInput(attrs={"min": "1", "placeholder": "e.g. 1"}),
            "recipient": forms.Select(),
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "amount": forms.NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "Payout amount in naira"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional note"}),
        }

    def clean_round_number(self):
        number = self.cleaned_data["round_number"]
        qs = AjoPayout.objects.filter(round_number=number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("That round number already exists. Choose another number.")
        return number
