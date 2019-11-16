from django import forms
from vendor.models import Product, Review, VendorQty
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ProductsAdd(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['stock', 'updated_at', 'created_at']


class VendorForm(forms.ModelForm):
    class Meta:
        model = VendorQty
        fields = ['qty']


def email_check(user):
    return user.is_vendor


class AddExisting(forms.Form):
    qty = forms.IntegerField()


class AddNew(forms.ModelForm):
    quantity = forms.IntegerField()

    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['qty', 'stock']


class VendorCreationForm(UserCreationForm):
    contact_number = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'contact_number']


class writereview(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Write about product', 'rows': '4', 'cols': '50'}))

    class Meta:
        model = Review
        fields = ['content']
