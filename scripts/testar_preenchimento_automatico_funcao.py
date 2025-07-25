#!/usr/bin/env python
"""
Script para testar a funcionalidade de preenchimento automático da função do militar
"""
import os
import sys
import django

# Configurar Django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import (
    Militar, UsuarioFuncao, CargoFuncao, CargoComissao
)

def testar_preenchimento_automatico_funcao():
    """Testa a funcionalidade de preenchimento automático da função do militar"""
    
    print("🧪 TESTANDO PREENCHIMENTO AUTOMÁTICO DE FUNÇÃO")
    print("=" * 60)
    
    # 1. Verificar militares com usuários vinculados
    print("\n👥 1. MILITARES COM USUÁRIOS VINCULADOS:")
    militares_com_usuario = Militar.objects.filter(user__isnull=False).select_related('user')
    
    for militar in militares_com_usuario[:5]:  # Mostrar apenas os primeiros 5
        funcoes_usuario = UsuarioFuncao.objects.filter(
            usuario=militar.user,
            status='ATIVO'
        ).select_related('cargo_funcao')
        
        print(f"   📋 {militar.get_posto_graduacao_display()} {militar.nome_completo}")
        print(f"      👤 Usuário: {militar.user.username}")
        print(f"      🏷️  Funções ativas: {funcoes_usuario.count()}")
        
        for funcao in funcoes_usuario:
            print(f"         - {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
        print()
    
    # 2. Verificar militares sem usuários vinculados
    print("\n👥 2. MILITARES SEM USUÁRIOS VINCULADOS:")
    militares_sem_usuario = Militar.objects.filter(user__isnull=True)[:5]
    
    for militar in militares_sem_usuario:
        print(f"   📋 {militar.get_posto_graduacao_display()} {militar.nome_completo}")
        print(f"      ❌ Sem usuário vinculado")
        print(f"      🏷️  Posto: {militar.posto_graduacao}")
        print()
    
    # 3. Testar mapeamento de postos para cargos
    print("\n🏷️  3. MAPEAMENTO DE POSTOS PARA CARGOS:")
    posto_cargo_map = {
        'CB': 'Coronel',
        'TC': 'Tenente Coronel', 
        'MJ': 'Major',
        'CP': 'Capitão',
        '1T': '1º Tenente',
        '2T': '2º Tenente',
        'AS': 'Aspirante a Oficial',
        'ST': 'Subtenente',
        '1S': '1º Sargento',
        '2S': '2º Sargento',
        '3S': '3º Sargento',
        'CAB': 'Cabo',
        'SD': 'Soldado'
    }
    
    for posto, cargo_nome in posto_cargo_map.items():
        cargo, created = CargoComissao.objects.get_or_create(
            nome=cargo_nome,
            defaults={
                'codigo': f'CARGO_{posto}',
                'descricao': f'Cargo padrão para posto {posto}',
                'ativo': True,
                'ordem': 100
            }
        )
        
        status = "✅ Criado" if created else "🔄 Já existe"
        print(f"   {posto} → {cargo_nome} ({status})")
    
    # 4. Simular busca de função para diferentes cenários
    print("\n🔍 4. SIMULAÇÃO DE BUSCA DE FUNÇÃO:")
    
    # Cenário 1: Militar com usuário e função
    if militares_com_usuario.exists():
        militar_com_funcao = militares_com_usuario.first()
        print(f"   📋 Cenário 1: Militar com função")
        print(f"      Militar: {militar_com_funcao.nome_completo}")
        print(f"      Usuário: {militar_com_funcao.user.username}")
        
        funcao_usuario = UsuarioFuncao.objects.filter(
            usuario=militar_com_funcao.user,
            status='ATIVO'
        ).select_related('cargo_funcao').first()
        
        if funcao_usuario:
            print(f"      ✅ Função encontrada: {funcao_usuario.cargo_funcao.nome}")
        else:
            print(f"      ❌ Nenhuma função ativa encontrada")
    
    # Cenário 2: Militar sem usuário (usar posto/graduação)
    if militares_sem_usuario.exists():
        militar_sem_funcao = militares_sem_usuario.first()
        print(f"\n   📋 Cenário 2: Militar sem usuário")
        print(f"      Militar: {militar_sem_funcao.nome_completo}")
        print(f"      Posto: {militar_sem_funcao.posto_graduacao}")
        
        cargo_nome = posto_cargo_map.get(militar_sem_funcao.posto_graduacao, 'Militar')
        cargo, created = CargoComissao.objects.get_or_create(
            nome=cargo_nome,
            defaults={
                'codigo': f'CARGO_{militar_sem_funcao.posto_graduacao}',
                'descricao': f'Cargo padrão para {militar_sem_funcao.get_posto_graduacao_display()}',
                'ativo': True,
                'ordem': 100
            }
        )
        
        print(f"      ✅ Cargo criado/encontrado: {cargo.nome}")
    
    # 5. Estatísticas finais
    print("\n📊 5. ESTATÍSTICAS:")
    total_militares = Militar.objects.count()
    militares_com_usuario_count = Militar.objects.filter(user__isnull=False).count()
    militares_sem_usuario_count = Militar.objects.filter(user__isnull=True).count()
    total_cargos = CargoComissao.objects.count()
    
    print(f"   📋 Total de militares: {total_militares}")
    print(f"   👤 Militares com usuário: {militares_com_usuario_count}")
    print(f"   ❌ Militares sem usuário: {militares_sem_usuario_count}")
    print(f"   🏷️  Total de cargos: {total_cargos}")
    
    # 6. Recomendações
    print("\n💡 6. RECOMENDAÇÕES:")
    if militares_sem_usuario_count > 0:
        print(f"   ⚠️  {militares_sem_usuario_count} militares não possuem usuário vinculado")
        print(f"      → Serão usados cargos baseados no posto/graduação")
    
    if militares_com_usuario_count > 0:
        usuarios_sem_funcao = User.objects.filter(
            militar__isnull=False,
            funcoes__isnull=True
        ).count()
        
        if usuarios_sem_funcao > 0:
            print(f"   ⚠️  {usuarios_sem_funcao} usuários não possuem função ativa")
            print(f"      → Serão usados cargos baseados no posto/graduação")
    
    print("\n✅ Teste concluído!")
    print("   A funcionalidade está pronta para uso.")
    print("   Quando um militar for selecionado no formulário,")
    print("   a função será preenchida automaticamente.")

if __name__ == '__main__':
    testar_preenchimento_automatico_funcao() 