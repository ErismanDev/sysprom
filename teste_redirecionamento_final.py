#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from datetime import datetime

def teste_redirecionamento_final():
    """Teste final para verificar a lógica de redirecionamento"""
    print("=== TESTE FINAL DE REDIRECIONAMENTO ===")
    
    # Simular dados do POST
    tipo = 'ANTIGUIDADE'
    categoria = 'PRACAS'  # Testando com praças
    data_promocao = datetime.now().date()
    
    print(f"DEBUG - Tipo: {tipo}")
    print(f"DEBUG - Categoria: {categoria}")
    print(f"DEBUG - Data: {data_promocao}")
    
    try:
        # Criar quadro (simulando a criação na view)
        novo_quadro = QuadroAcesso.objects.create(
            tipo=tipo,
            categoria=categoria,
            data_promocao=data_promocao,
            status='EM_ELABORACAO',
            observacoes=f"Quadro de {tipo.lower()} para {categoria.lower()} - {data_promocao.strftime('%d/%m/%Y')} - Inclui todos os postos"
        )
        
        print(f"DEBUG - Quadro criado com ID: {novo_quadro.pk}")
        print(f"DEBUG - Categoria do quadro: {novo_quadro.categoria}")
        
        # Simular a lógica de redirecionamento da view
        print(f"DEBUG - Verificando categoria: {novo_quadro.categoria}")
        print(f"DEBUG - É igual a 'PRACAS'? {novo_quadro.categoria == 'PRACAS'}")
        
        if novo_quadro.categoria == 'PRACAS':
            print("✓ Redirecionando para praças: quadro_acesso_pracas_detail")
            url_esperada = f'/militares/pracas/quadros-acesso/{novo_quadro.pk}/'
            print(f"✓ URL esperada: {url_esperada}")
        else:
            print("✓ Redirecionando para oficiais: quadro_acesso_detail")
            url_esperada = f'/militares/quadros-acesso/{novo_quadro.pk}/'
            print(f"✓ URL esperada: {url_esperada}")
        
        # Verificar se o quadro foi salvo corretamente
        quadro_recuperado = QuadroAcesso.objects.get(pk=novo_quadro.pk)
        print(f"DEBUG - Quadro recuperado do banco:")
        print(f"  - ID: {quadro_recuperado.pk}")
        print(f"  - Categoria: {quadro_recuperado.categoria}")
        print(f"  - Tipo: {quadro_recuperado.tipo}")
        print(f"  - Data: {quadro_recuperado.data_promocao}")
        
        # Testar a função gerar_quadro_completo
        print(f"\nDEBUG - Testando gerar_quadro_completo...")
        sucesso, mensagem = novo_quadro.gerar_quadro_completo()
        print(f"DEBUG - Sucesso: {sucesso}")
        print(f"DEBUG - Mensagem: {mensagem}")
        
        # Verificar se a categoria foi alterada após gerar_quadro_completo
        quadro_apos_geracao = QuadroAcesso.objects.get(pk=novo_quadro.pk)
        print(f"DEBUG - Categoria após gerar_quadro_completo: {quadro_apos_geracao.categoria}")
        
        if quadro_apos_geracao.categoria == 'PRACAS':
            print("✓ Categoria permaneceu 'PRACAS' após gerar_quadro_completo")
            print("✓ Redirecionamento correto seria para praças")
        else:
            print(f"✗ ERRO: Categoria foi alterada para '{quadro_apos_geracao.categoria}' após gerar_quadro_completo")
        
        # Limpar quadro de teste
        novo_quadro.delete()
        print("✓ Quadro de teste removido")
        
    except Exception as e:
        print(f"✗ ERRO: {str(e)}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    teste_redirecionamento_final() 