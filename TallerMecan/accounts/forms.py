from django import forms
from .models import Item, Stock,ServiceType

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price']

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['item', 'amount', 'location']
class InvoiceForm(forms.Form):
    service_type = forms.ModelChoiceField(queryset=ServiceType.objects.all(), label="Tipo de Servicio")
    license_plate = forms.CharField(label="Placa", max_length=20)