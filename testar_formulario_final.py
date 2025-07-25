#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from militares.forms import QuadroAcessoForm
from militares.views_pracas import calcular_proxima_data_promocao_pracas
from datetime import date

def testar_formulario_final():
    print("=== TESTE FINAL DO FORMULÁRIO ===\n")
    
    # 1. Testar criação de formulário
    print("1. TESTANDO CRIAÇÃO DE FORMULÁRIO:")
    print("-" * 50)
    
    form = QuadroAcessoForm()
    print(f"Campo tipo inicial: {form.fields['tipo'].initial}")
    print(f"Campo status inicial: {form.fields['status'].initial}")
    print(f"Campo status widget: {form.fields['status'].widget}")
    
    # 2. Testar validação com dados válidos
    print(f"\n2. TESTANDO VALIDAÇÃO COM DADOS VÁLIDOS:")
    print("-" * 50)
    
    data_futura = date(2026, 7, 18)
    dados_validos = {
        'tipo': 'ANTIGUIDADE',
        'data_promocao': data_futura,
        'status': 'EM_ELABORACAO',
        'observacoes': 'Teste de formulário'
    }
    
    form = QuadroAcessoForm(dados_validos)
    print(f"Formulário válido: {form.is_valid()}")
    
    if form.is_valid():
        print("✅ Formulário válido!")
        print(f"Tipo: {form.cleaned_data['tipo']}")
        print(f"Data: {form.cleaned_data['data_promocao']}")
        print(f"Status: {form.cleaned_data['status']}")
    else:
        print("❌ Formulário inválido!")
        print(f"Erros: {form.errors}")
    
    # 3. Testar validação com dados duplicados
    print(f"\n3. TESTANDO VALIDAÇÃO COM DADOS DUPLICADOS:")
    print("-" * 50)
    
    # Usar uma data que já existe
    data_existente = date(2025, 7, 18)
    dados_duplicados = {
        'tipo': 'ANTIGUIDADE',
        'data_promocao': data_existente,
        'status': 'EM_ELABORACAO',
        'observacoes': 'Teste duplicado'
    }
    
    form = QuadroAcessoForm(dados_duplicados)
    print(f"Formulário válido: {form.is_valid()}")
    
    if not form.is_valid():
        print("✅ Formulário corretamente rejeitado!")
        print(f"Erros: {form.errors}")
    else:
        print("❌ Formulário deveria ser inválido!")
    
    # 4. Testar criação real de quadro
    print(f"\n4. TESTANDO CRIAÇÃO REAL DE QUADRO:")
    print("-" * 50)
    
    try:
        # Verificar se já existe
        if QuadroAcesso.objects.filter(tipo='ANTIGUIDADE', data_promocao=data_futura).exists():
            print(f"Já existe quadro para {data_futura.strftime('%d/%m/%Y')}")
            data_futura = date(2026, 12, 25)
        
        quadro = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            data_promocao=data_futura,
            status='EM_ELABORACAO'
        )
        print(f"✅ Quadro criado com sucesso! ID: {quadro.id}")
        
        # Testar geração
        sucesso, mensagem = quadro.gerar_quadro_completo()
        print(f"Geração: {sucesso} - {mensagem}")
        
        # Limpar
        quadro.delete()
        print("✅ Quadro de teste removido")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # 5. Resumo das correções
    print(f"\n5. RESUMO DAS CORREÇÕES IMPLEMENTADAS:")
    print("-" * 50)
    print("✅ Campo status definido como hidden com valor padrão")
    print("✅ Validação de duplicatas implementada na view")
    print("✅ Mensagens de erro melhoradas")
    print("✅ Template atualizado com informações úteis")
    print("✅ Scripts de limpeza e teste criados")
    
    print(f"\n6. PRÓXIMOS PASSOS:")
    print("-" * 50)
    print("1. Acesse o formulário via interface web")
    print("2. Use uma data futura diferente das existentes")
    print("3. Ou edite um quadro existente")
    print("4. O sistema agora deve funcionar corretamente!")

if __name__ == "__main__":
    testar_formulario_final() 