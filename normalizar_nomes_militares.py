#!/usr/bin/env python
"""
Script para normalizar nomes dos militares no banco de dados
Remove diferenças de maiúsculas/minúsculas e caracteres especiais
"""

import os
import sys
import django
import unicodedata
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def normalizar_texto(texto):
    """
    Normaliza texto removendo acentos e convertendo para maiúsculas
    """
    if not texto:
        return texto
    
    # Converter para string se não for
    texto = str(texto)
    
    # Normalizar caracteres Unicode (NFD = decomposição)
    texto = unicodedata.normalize('NFD', texto)
    
    # Remover acentos (diacríticos)
    texto = ''.join(char for char in texto if not unicodedata.combining(char))
    
    # Converter para maiúsculas
    texto = texto.upper()
    
    # Remover caracteres especiais, mantendo apenas letras, números e espaços
    texto = re.sub(r'[^A-Z0-9\s]', '', texto)
    
    # Remover espaços múltiplos
    texto = re.sub(r'\s+', ' ', texto)
    
    # Remover espaços no início e fim
    texto = texto.strip()
    
    return texto

def verificar_nomes_nao_normalizados():
    """
    Verifica nomes que não estão normalizados
    """
    print("🔍 Verificando nomes não normalizados...")
    
    militares = Militar.objects.all()
    problemas_encontrados = []
    
    for militar in militares:
        nome_original = militar.nome_completo
        nome_normalizado = normalizar_texto(nome_original)
        
        if nome_original != nome_normalizado:
            problemas_encontrados.append({
                'id': militar.id,
                'nome_original': nome_original,
                'nome_normalizado': nome_normalizado,
                'matricula': militar.matricula
            })
    
    return problemas_encontrados

def normalizar_nomes_militares():
    """
    Normaliza os nomes dos militares no banco de dados
    """
    print("🔧 Normalizando nomes dos militares...")
    
    militares = Militar.objects.all()
    total_corrigidos = 0
    
    for militar in militares:
        alterado = False
        
        # Normalizar nome_completo
        nome_original = militar.nome_completo
        nome_normalizado = normalizar_texto(nome_original)
        
        if nome_original != nome_normalizado:
            militar.nome_completo = nome_normalizado
            alterado = True
            print(f"  ✅ Militar ID {militar.id} ({militar.matricula}):")
            print(f"     Original: {nome_original}")
            print(f"     Normalizado: {nome_normalizado}")
        
        # Normalizar nome_guerra (se existir)
        if militar.nome_guerra:
            nome_guerra_original = militar.nome_guerra
            nome_guerra_normalizado = normalizar_texto(nome_guerra_original)
            
            if nome_guerra_original != nome_guerra_normalizado:
                militar.nome_guerra = nome_guerra_normalizado
                alterado = True
                print(f"     Nome Guerra:")
                print(f"       Original: {nome_guerra_original}")
                print(f"       Normalizado: {nome_guerra_normalizado}")
        
        if alterado:
            militar.save()
            total_corrigidos += 1
    
    return total_corrigidos

def criar_backup_antes_normalizacao():
    """
    Cria um backup dos nomes antes da normalização
    """
    print("💾 Criando backup dos nomes antes da normalização...")
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_nomes_antes_normalizacao_{timestamp}.txt"
    
    try:
        # Criar diretório de backup se não existir
        os.makedirs("backups", exist_ok=True)
        
        militares = Militar.objects.all()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("BACKUP DOS NOMES ANTES DA NORMALIZAÇÃO\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            for militar in militares:
                f.write(f"ID: {militar.id}\n")
                f.write(f"Matrícula: {militar.matricula}\n")
                f.write(f"Nome Completo: {militar.nome_completo}\n")
                f.write(f"Nome Guerra: {militar.nome_guerra}\n")
                f.write("-" * 30 + "\n")
        
        print(f"✅ Backup criado: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def mostrar_exemplos_normalizacao():
    """
    Mostra exemplos de como os nomes serão normalizados
    """
    print("📋 Exemplos de normalização:")
    print("=" * 50)
    
    exemplos = [
        "JAMMES MagalhÒes Silva",
        "Johnathan PatrÝcio Cavalcante SEIXAS",
        "MoisÚs Andrade Fernandes CANTU┴RIO",
        "Ant¶nio JosÚ de Melo LIMA",
        "JosÚ AUGUSTO Soares da Cruz",
        "LuÝs de Morais NUNES",
        "ODAIR JosÚ da Silva Santos",
        "VinÝcius EDUARDO Santos Martins",
        "LUCIANA LÝs de Souza e Santos",
        "K┴CIA LÝgia Silveira Linhares",
        "JoÒo Bezerra NOVAES Neto",
        "JosuÚ FELICIANO de Melo",
        "Manoel Antonio de FRANÃA J┌NIOR",
        "Albert Moreira de MENDONÃA",
        "APARISA Maria CoÛlho dos Santos",
        "Bruno GONÃALVES Costa",
        "Erida THAYNARA AssunþÒo Ara·jo da Silva",
        "FabrÝcio de MOURA Medeiros",
        "James Rodrigues de FRANÃA",
        "LaÚcio WILSON Cordato Pereira",
        "RÈMULO Castelo Branco Bezerra Filho",
        "EM═DIO JosÚ Medeiros de Oliveira",
        "JosÚ VELOSO Soares",
        "JosuÚ Clementino de MOURA",
        "DIÈGO Martins Fonseca Neto",
        "JosÚ EPIT┴CIO da Silva Filho",
        "JosÚ Francisco Alves da VERA CRUZ",
        "JosÚ LIMA FILHO",
        "JosÚ NILTON da Costa",
        "JUAREZ JosÚ  de Sousa J·nior",
        "MARCOS PAULO de ArÛa Lira",
        "SebastiÒo DOMINGOS de Carvalho Filho",
        "SÚrgio Henrique Reis de ARAG├O",
        "WILLIAM BorgÚa Lima",
        "JosÚ ERISMAN de Sousa",
        "ABIMAEL HONËRIO CORREIA J┌NIOR",
        "ANTÈNIO MELO",
        "EDSON FRANÃA SILVA DE SOUSA",
        "FRANCISCO SANTHIAGO HOLANDA FRANÃA SILVA",
        "JO├O MARCOS DE ARA┌JO ESCËRCIO",
        "MARÃANIO ALVES MARQUES",
        "MÈNICA LET═CIA ALVES CARDOSO",
        "OZIAS GONÃALVES LIMA J┌NIOR",
        "╔RICO VinÝcius Mendes da Silva",
        "ANTÈNIO CARLOS de Sousa Santos",
        "DÔmaro ST╩NIO Melo Viana",
        "JoÒo Batista NERY de Sousa",
        "JoÒo de SOUSA Monteiro NETO",
        "JosÚ Francisco de ARA┌JO Silva",
        "JosÚ FRAZ├O de Moura Filho",
        "LuÝz Alves da Vera CRUZ",
        "MARCIO RogÚrio Bernardes da Rocha",
        "GlÚcio MENDES da Rocha"
    ]
    
    for exemplo in exemplos:
        normalizado = normalizar_texto(exemplo)
        print(f"Original: {exemplo}")
        print(f"Normalizado: {normalizado}")
        print("-" * 40)

if __name__ == '__main__':
    print("🔧 Script de Normalização de Nomes dos Militares")
    print("=" * 60)
    
    # Mostrar exemplos de normalização
    mostrar_exemplos_normalizacao()
    
    print("\n" + "=" * 60)
    
    # Verificar nomes não normalizados
    problemas = verificar_nomes_nao_normalizados()
    
    if problemas:
        print(f"\n⚠️  Encontrados {len(problemas)} nomes não normalizados")
        
        # Mostrar alguns exemplos
        print("\n📋 Exemplos de nomes que serão normalizados:")
        for i, problema in enumerate(problemas[:10]):  # Mostrar apenas os primeiros 10
            print(f"  {i+1}. ID {problema['id']} ({problema['matricula']}):")
            print(f"     Original: {problema['nome_original']}")
            print(f"     Normalizado: {problema['nome_normalizado']}")
        
        if len(problemas) > 10:
            print(f"  ... e mais {len(problemas) - 10} nomes")
        
        # Perguntar se deve normalizar
        resposta = input("\nDeseja normalizar os nomes dos militares? (s/n): ").lower()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            # Criar backup antes da normalização
            if criar_backup_antes_normalizacao():
                # Normalizar nomes
                total_corrigidos = normalizar_nomes_militares()
                print(f"\n✅ Normalização concluída! {total_corrigidos} militares corrigidos.")
            else:
                print("\n❌ Backup não foi criado. Normalização cancelada por segurança.")
        else:
            print("\n❌ Operação cancelada pelo usuário.")
    else:
        print("\n✅ Todos os nomes já estão normalizados!") 