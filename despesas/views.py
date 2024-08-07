from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import GrupoDespesas, Despesa
from django.http import JsonResponse
from django.middleware import csrf
from django.utils.dateparse import parse_date
from django.db.models import Sum
from datetime import datetime
from django.db.models.functions import TruncMonth
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64

def grupo_despesas_form(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            GrupoDespesas.objects.create(nome=nome)
            return redirect('grupo_despesas_form')
    
    grupos = GrupoDespesas.objects.all()
    return render(request, 'grupo_despesas_form.html', {'grupos': grupos})

def despesa_form(request):
    if request.method == 'POST':
        grupo_id = request.POST.get('grupo_id')
        nome = request.POST.get('nome')
        vencimento = request.POST.get('vencimento')
        valor = request.POST.get('valor')
        data_pagamento = request.POST.get('data_pagamento')
        valor_pago = request.POST.get('valor_pago')
        observacao = request.POST.get('observacao')

        try:
            despesa = Despesa(
                grupo_id=grupo_id,
                nome=nome,
                vencimento=vencimento,
                valor=valor,
                data_pagamento=data_pagamento if data_pagamento else None,
                valor_pago=valor_pago if valor_pago else None,
                observacao=observacao
            )
            despesa.full_clean()
            despesa.save()
            return redirect('despesa_form')
        except ValidationError as e:
            return render(request, 'despesa_form.html', {'grupos': GrupoDespesas.objects.all(), 'errors': e.messages})

    grupos = GrupoDespesas.objects.all()
    return render(request, 'despesa_form.html', {'grupos': grupos})

def listar_despesas(request):
    filtro_nome = request.GET.get('filtro_nome', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    filtro_estado = request.GET.get('filtro_estado', 'todas')
    filtro_grupo = request.GET.get('filtro_grupo', '')

    despesas = Despesa.objects.all().order_by('-vencimento')

    if filtro_nome:
        despesas = despesas.filter(nome__icontains=filtro_nome)

    if data_inicio:
        data_inicio = parse_date(data_inicio)
        if data_inicio:
            despesas = despesas.filter(vencimento__gte=data_inicio)

    if data_fim:
        data_fim = parse_date(data_fim)
        if data_fim:
            despesas = despesas.filter(vencimento__lte=data_fim)

    if filtro_estado == 'abertas':
        despesas = despesas.filter(data_pagamento__isnull=True)
    elif filtro_estado == 'pagas':
        despesas = despesas.filter(data_pagamento__isnull=False)

    if filtro_grupo:
        despesas = despesas.filter(grupo_id=filtro_grupo)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        despesas_list = [
            {
                'id': despesa.id,
                'nome': despesa.nome,
                'grupo': despesa.grupo.nome,
                'vencimento': despesa.vencimento.strftime('%Y-%m-%d'),
                'valor': despesa.valor,
                'data_pagamento': despesa.data_pagamento.strftime('%Y-%m-%d') if despesa.data_pagamento else '',
                'valor_pago': despesa.valor_pago if despesa.valor_pago else '0.00',
                'observacao': despesa.observacao,
            }
            for despesa in despesas
        ]
        return JsonResponse({'despesas': despesas_list, 'csrf_token': csrf.get_token(request)})
    
    grupos = GrupoDespesas.objects.all()
    return render(request, 'listagem.html', {'despesas': despesas, 'grupos': grupos})

def excluir_despesa(request, despesa_id):
    despesa = get_object_or_404(Despesa, pk=despesa_id)
    
    if request.method == 'POST':
        despesa.delete()
        return redirect('listagem')

    return redirect('listagem')

def alterar_despesa(request, despesa_id):
    despesa = get_object_or_404(Despesa, pk=despesa_id)
    grupos = GrupoDespesas.objects.all()

    if request.method == 'POST':
        despesa.grupo_id = request.POST.get('grupo_id')
        despesa.nome = request.POST.get('nome')
        despesa.vencimento = request.POST.get('vencimento')
        despesa.valor = request.POST.get('valor')

        data_pagamento = request.POST.get('data_pagamento')
        despesa.data_pagamento = data_pagamento if data_pagamento else None

        valor_pago = request.POST.get('valor_pago')
        despesa.valor_pago = valor_pago if valor_pago else None

        despesa.observacao = request.POST.get('observacao')
        
        despesa.save()
        return redirect('listagem')

    return render(request, 'alterar.html', {'despesa': despesa, 'grupos': grupos})

def excluir_grupo_despesas(request, grupo_id):
    grupo = get_object_or_404(GrupoDespesas, pk=grupo_id)

    if request.method == 'POST':
        grupo.delete()
        return redirect('grupo_despesas_form')

    return redirect('grupo_despesas_form')

def alterar_grupo_despesas(request, grupo_id):
    grupo = get_object_or_404(GrupoDespesas, pk=grupo_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            grupo.nome = nome
            grupo.save()
            return redirect('grupo_despesas_form')
    
    return render(request, 'alterar_grupo_despesas.html', {'grupo': grupo})

def relatorios(request):
    return render(request, 'relatorios.html')

def relatorio_despesas_por_grupo(request):
    grupo_id = request.GET.get('grupo_id')
    total_pago = None
    total_em_aberto = None
    percentual = None
    despesas_pagas_por_mes = []
    despesas_abertas_por_mes = []

    grupos = GrupoDespesas.objects.all()

    if grupo_id:
        despesas_grupo = Despesa.objects.filter(grupo_id=grupo_id)

        despesas_pagas = despesas_grupo.filter(data_pagamento__isnull=False).annotate(month=TruncMonth('vencimento')).values('month').annotate(total=Sum('valor')).order_by('month')
        despesas_abertas = despesas_grupo.filter(data_pagamento__isnull=True).annotate(month=TruncMonth('vencimento')).values('month').annotate(total=Sum('valor')).order_by('month')
        
        #Dados do Gráfico
        meses = sorted(set(despesa['month'] for despesa in despesas_pagas) | set(despesa['month'] for despesa in despesas_abertas))
        despesas_pagas_por_mes = {mes: 0 for mes in meses}
        despesas_abertas_por_mes = {mes: 0 for mes in meses}

        for despesa in despesas_pagas:
            despesas_pagas_por_mes[despesa['month']] = despesa['total']

        for despesa in despesas_abertas:
            despesas_abertas_por_mes[despesa['month']] = despesa['total']

        meses = [mes.strftime('%m/%Y') for mes in meses]
        valores_pagos = [despesas_pagas_por_mes[mes] for mes in despesas_pagas_por_mes]
        valores_abertos = [despesas_abertas_por_mes[mes] for mes in despesas_abertas_por_mes]

        #Gráfico de Barras
        x = range(len(meses))

        plt.figure(figsize=(10, 5))
        plt.bar(x, valores_pagos, width=0.4, label='Despesas Pagas', align='center')
        plt.bar(x, valores_abertos, width=0.4, label='Despesas Abertas', align='edge')
        plt.xlabel('Mês de Vencimento')
        plt.ylabel('Valor R$')
        plt.title('Despesas Pagas e Abertas por Mês')
        plt.legend()
        plt.xticks(ticks=x, labels=meses, rotation=45)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        grafico_base64 = base64.b64encode(image_png).decode('utf-8')

        despesas_grupo_total_pago = despesas_grupo.filter(data_pagamento__isnull=False).aggregate(total=Sum('valor_pago'))['total'] or 0
        total_geral_pago = Despesa.objects.filter(data_pagamento__isnull=False).aggregate(total=Sum('valor_pago'))['total'] or 0

        if total_geral_pago > 0:
            percentual = round((despesas_grupo_total_pago / total_geral_pago) * 100, 2)

        total_pago = round(despesas_grupo_total_pago, 2)
        total_em_aberto = round(despesas_grupo.filter(data_pagamento__isnull=True).aggregate(total=Sum('valor'))['total'] or 0, 2)

    context = {
        'grupos': grupos,
        'total_pago': total_pago,
        'total_em_aberto': total_em_aberto,
        'percentual': percentual,
        'grupo_id': grupo_id,
        'grafico_base64': grafico_base64 if grupo_id else None,
    }

    return render(request, 'relatorio_despesas_por_grupo.html', context)