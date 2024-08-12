from django.urls import path
from despesas import views

urlpatterns = [
    path('grupo_despesas/', views.grupo_despesas_form, name='grupo_despesas_form'),
    path('despesa/', views.despesa_form, name='despesa_form'),
    path('listagem/', views.listar_despesas, name='listagem'),
    path('excluir_despesa/<int:despesa_id>/', views.excluir_despesa, name='excluir_despesa'),
    path('alterar_despesa/<int:despesa_id>/', views.alterar_despesa, name='alterar_despesa'),
    path('excluir_grupo_despesas/<int:grupo_id>/', views.excluir_grupo_despesas, name='excluir_grupo_despesas'),
    path('alterar_grupo_despesas/<int:grupo_id>/', views.alterar_grupo_despesas, name='alterar_grupo_despesas'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorio_despesas_por_grupo/', views.relatorio_despesas_por_grupo, name='relatorio_despesas_por_grupo'),
    path('relatorio_geral/', views.relatorio_geral, name='relatorio_geral'),
]
