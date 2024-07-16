from django import forms
from .models import GrupoDespesas, Despesa

class GrupoDespesasForm(forms.ModelForm):
    class Meta:
        model = GrupoDespesas
        fields = ['nome']

class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = ['grupo', 'nome', 'vencimento', 'valor', 'data_pagamento', 'valor_pago', 'observacao']
        
    grupo = forms.ModelChoiceField(queryset=GrupoDespesas.objects.all(), empty_label="Selecione um grupo")
    nome = forms.CharField(max_length=100)
    vencimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    valor = forms.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    valor_pago = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    observacao = forms.CharField(widget=forms.Textarea, required=False)
