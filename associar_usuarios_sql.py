#!/usr/bin/env python3
"""
Script para gerar SQL de associação de usuários aos militares
"""

import os
import sys
import django
from datetime import datetime

def configurar_ambiente():
    """Configura o ambiente para acessar o banco local"""
    print("🌐 Configurando ambiente local...")
    
    # Configurar variáveis de ambiente para banco local
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings'
    
    try:
        django.setup()
        print("✅ Ambiente local configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar ambiente: {e}")
        return False

def gerar_sql_associacao():
    """Gera SQL para associar usuários aos militares"""
    print("\n🔗 Gerando SQL de associação...")
    
    try:
        from django.contrib.auth.models import User
        from militares.models import Militar
        
        # Buscar todos os usuários
        usuarios = User.objects.all()
        
        sql_associacoes = []
        sql_associacoes.append("-- ========================================")
        sql_associacoes.append("-- ASSOCIAÇÃO DE USUÁRIOS AOS MILITARES")
        sql_associacoes.append("-- ========================================")
        sql_associacoes.append("")
        
        associacoes_realizadas = 0
        usuarios_nao_associados = 0
        
        for usuario in usuarios:
            militar_encontrado = None
            
            # Tentar encontrar militar por CPF (username)
            try:
                militar_encontrado = Militar.objects.get(cpf=usuario.username)
            except Militar.DoesNotExist:
                pass
            
            # Se não encontrou por CPF, tentar por nome completo
            if not militar_encontrado:
                nome_completo = f"{usuario.first_name} {usuario.last_name}".strip()
                if nome_completo:
                    try:
                        militar_encontrado = Militar.objects.get(nome_completo__iexact=nome_completo)
                    except Militar.DoesNotExist:
                        pass
            
            # Se não encontrou por nome, tentar por email
            if not militar_encontrado and usuario.email:
                try:
                    militar_encontrado = Militar.objects.get(email__iexact=usuario.email)
                except Militar.DoesNotExist:
                    pass
            
            # Se encontrou militar, gerar SQL de associação
            if militar_encontrado and not militar_encontrado.user:
                sql = f"-- Associar usuário {usuario.username} ao militar {militar_encontrado.nome_completo}"
                sql_associacoes.append(sql)
                sql = f"UPDATE militares_militar SET user_id = {usuario.id} WHERE id = {militar_encontrado.id};"
                sql_associacoes.append(sql)
                sql_associacoes.append("")
                associacoes_realizadas += 1
            else:
                usuarios_nao_associados += 1
                sql = f"-- Usuário {usuario.username} não pôde ser associado automaticamente"
                sql_associacoes.append(sql)
                sql_associacoes.append("")
        
        # Adicionar resumo
        sql_associacoes.append("-- ========================================")
        sql_associacoes.append("-- RESUMO DA ASSOCIAÇÃO")
        sql_associacoes.append("-- ========================================")
        sql_associacoes.append(f"-- Total de associações realizadas: {associacoes_realizadas}")
        sql_associacoes.append(f"-- Usuários não associados: {usuarios_nao_associados}")
        sql_associacoes.append("")
        sql_associacoes.append("-- Verificar associações")
        sql_associacoes.append("SELECT COUNT(*) as total_militares_com_usuario FROM militares_militar WHERE user_id IS NOT NULL;")
        sql_associacoes.append("SELECT COUNT(*) as total_militares_sem_usuario FROM militares_militar WHERE user_id IS NULL;")
        
        print(f"📊 Associações geradas: {associacoes_realizadas}")
        print(f"📊 Usuários não associados: {usuarios_nao_associados}")
        
        return sql_associacoes
        
    except Exception as e:
        print(f"❌ Erro ao gerar SQL de associação: {e}")
        return []

def gerar_arquivo_sql():
    """Gera o arquivo SQL de associação"""
    print("\n📝 Gerando arquivo SQL de associação...")
    
    try:
        # Configurar ambiente
        if not configurar_ambiente():
            return False
        
        # Gerar SQL de associação
        sql_associacoes = gerar_sql_associacao()
        
        if not sql_associacoes:
            print("❌ Nenhuma associação foi gerada")
            return False
        
        # Salvar arquivo
        nome_arquivo = f"associacao_usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_associacoes))
        
        print(f"✅ Arquivo SQL de associação gerado: {nome_arquivo}")
        print(f"📊 Total de linhas SQL: {len(sql_associacoes)}")
        
        # Mostrar instruções
        print("\n" + "=" * 60)
        print("📋 INSTRUÇÕES PARA ASSOCIAÇÃO:")
        print("=" * 60)
        print("1. Execute primeiro o script de migração principal")
        print("2. Acesse o painel do Supabase")
        print("3. Vá para SQL Editor")
        print("4. Abra o arquivo de associação gerado")
        print("5. Cole todo o conteúdo no editor SQL")
        print("6. Execute o script")
        print("7. Verifique se as associações foram realizadas")
        print()
        print("⚠️  IMPORTANTE:")
        print("- Execute este script APÓS a migração principal")
        print("- Verifique se os usuários e militares foram inseridos")
        print("- As associações são feitas por CPF, nome ou email")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar arquivo SQL: {e}")
        return False

def main():
    """Função principal"""
    print("🔗 GERADOR DE SQL DE ASSOCIAÇÃO")
    print("=" * 60)
    
    if gerar_arquivo_sql():
        print("\n🎉 Geração de SQL de associação concluída com sucesso!")
        return True
    else:
        print("\n❌ Falha na geração do SQL de associação")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Operação falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 