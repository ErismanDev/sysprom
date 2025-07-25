#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from militares.views_pracas import calcular_proxima_data_promocao_pracas
from datetime import date, timedelta

def testar_criacao_quadro():
    print("=== TESTANDO CRIAÇÃO DE QUADRO ===\n")
    
    # 1. Verificar datas existentes
    print("1. DATAS EXISTENTES:")
    print("-" * 50)
    
    datas_existentes = QuadroAcesso.objects.values_list('data_promocao', flat=True).distinct()
    for data_existente in datas_existentes:
        print(f"  {data_existente.strftime('%d/%m/%Y')}")
    
    # 2. Calcular próxima data
    print(f"\n2. PRÓXIMA DATA CALCULADA:")
    print("-" * 50)
    
    proxima_data = calcular_proxima_data_promocao_pracas()
    print(f"Próxima data: {proxima_data.strftime('%d/%m/%Y')}")
    
    # 3. Verificar se já existe quadro para esta data
    print(f"\n3. VERIFICANDO EXISTÊNCIA:")
    print("-" * 50)
    
    quadros_existentes = QuadroAcesso.objects.filter(data_promocao=proxima_data)
    print(f"Quadros existentes para {proxima_data.strftime('%d/%m/%Y')}: {quadros_existentes.count()}")
    
    for quadro in quadros_existentes:
        print(f"  ID: {quadro.id}, Tipo: {quadro.tipo}, Status: {quadro.status}")
    
    # 4. Tentar criar um quadro com data diferente
    print(f"\n4. TESTANDO CRIAÇÃO COM DATA DIFERENTE:")
    print("-" * 50)
    
    # Usar uma data futura (próximo ano)
    data_teste = date(2026, 7, 18)
    
    # Verificar se existe
    if QuadroAcesso.objects.filter(data_promocao=data_teste).exists():
        print(f"Já existe quadro para {data_teste.strftime('%d/%m/%Y')}")
        data_teste = date(2026, 12, 25)
    
    print(f"Tentando criar quadro para: {data_teste.strftime('%d/%m/%Y')}")
    
    try:
        quadro_teste = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            data_promocao=data_teste,
            status='EM_ELABORACAO'
        )
        print(f"✅ Quadro criado com sucesso! ID: {quadro_teste.id}")
        
        # 5. Testar geração do quadro
        print(f"\n5. TESTANDO GERAÇÃO DO QUADRO:")
        print("-" * 50)
        
        sucesso, mensagem = quadro_teste.gerar_quadro_completo()
        print(f"Resultado: {sucesso}")
        print(f"Mensagem: {mensagem}")
        
        if sucesso:
            itens = quadro_teste.itemquadroacesso_set.count()
            print(f"Total de itens gerados: {itens}")
            
            if itens > 0:
                print("Primeiros 3 itens:")
                for item in quadro_teste.itemquadroacesso_set.all()[:3]:
                    print(f"  {item.posicao}. {item.militar.nome_completo} ({item.militar.posto_graduacao})")
        
        # 6. Limpar o quadro de teste
        print(f"\n6. LIMPANDO QUADRO DE TESTE:")
        print("-" * 50)
        quadro_teste.delete()
        print("✅ Quadro de teste removido")
        
    except Exception as e:
        print(f"❌ Erro ao criar quadro: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 7. Sugestões
    print(f"\n7. SUGESTÕES:")
    print("-" * 50)
    print("Para criar um novo quadro de acesso para praças:")
    print("1. Use uma data diferente das existentes")
    print("2. Ou edite um quadro existente")
    print("3. Ou exclua um quadro existente primeiro")
    print("\nDatas sugeridas para teste:")
    print(f"  - {date(2026, 7, 18).strftime('%d/%m/%Y')}")
    print(f"  - {date(2026, 12, 25).strftime('%d/%m/%Y')}")

if __name__ == "__main__":
    testar_criacao_quadro() 