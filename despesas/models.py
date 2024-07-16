from django.db import models

class GrupoDespesas(models.Model):
    nome = models.CharField(max_length=100, null=False)  

    class Meta:
        db_table = 'grupodespesas'  
        
    def __str__(self):
        return self.nome

class Despesa(models.Model):
    grupo = models.ForeignKey(GrupoDespesas, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    vencimento = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        managed = False
        db_table = 'despesa'
