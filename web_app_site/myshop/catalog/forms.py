from django import forms
from django.contrib.auth import get_user_model

# Получаем модель User
User = get_user_model()

class CartAddProductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super(CartAddProductForm, self).__init__(*args, **kwargs)
        if product:
            self.fields['quantity'] = forms.TypedChoiceField(
                choices=[(i, str(i)) for i in range(1, product.stock + 1)],
                coerce=int,
                initial=1
            )
        self.fields['override'] = forms.BooleanField(
            required=False, initial=False, widget=forms.HiddenInput
        )

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = User  # Используем модель User вместо Customer
        fields = ['first_name', 'last_name', 'email']

    # Добавляем дополнительные поля, которых нет в модели User
    address = forms.CharField(required=True, max_length=250, label="Адрес")
    postal_code = forms.CharField(required=True, max_length=20, label="Почтовый индекс")
    city = forms.CharField(required=True, max_length=100, label="Город")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user