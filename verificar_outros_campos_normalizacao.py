#!/usr/bin/env python
"""
Script para verificar outros campos que podem precisar de normalização
"""

import os
import sys
import django
import unicodedata
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import *

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

def verificar_campos_nao_normalizados():
    """
    Verifica outros campos que podem precisar de normalização
    """
    print("🔍 Verificando outros campos que podem precisar de normalização...")
    
    problemas_encontrados = []
    
    # Verificar CargoComissao
    print("\n📋 Verificando CargoComissao...")
    cargos = CargoComissao.objects.all()
    
    for cargo in cargos:
        if cargo.nome:
            nome_original = cargo.nome
            nome_normalizado = normalizar_texto(nome_original)
            
            if nome_original != nome_normalizado:
                problemas_encontrados.append({
                    'modelo': 'CargoComissao',
                    'id': cargo.id,
                    'campo': 'nome',
                    'original': nome_original,
                    'normalizado': nome_normalizado
                })
        
        if cargo.descricao:
            desc_original = cargo.descricao
            desc_normalizada = normalizar_texto(desc_original)
            
            if desc_original != desc_normalizada:
                problemas_encontrados.append({
                    'modelo': 'CargoComissao',
                    'id': cargo.id,
                    'campo': 'descricao',
                    'original': desc_original,
                    'normalizado': desc_normalizada
                })
    
    # Verificar ComissaoPromocao
    print("📋 Verificando ComissaoPromocao...")
    comissoes = ComissaoPromocao.objects.all()
    
    for comissao in comissoes:
        if comissao.nome:
            nome_original = comissao.nome
            nome_normalizado = normalizar_texto(nome_original)
            
            if nome_original != nome_normalizado:
                problemas_encontrados.append({
                    'modelo': 'ComissaoPromocao',
                    'id': comissao.id,
                    'campo': 'nome',
                    'original': nome_original,
                    'normalizado': nome_normalizado
                })
        
        if comissao.observacoes:
            obs_original = comissao.observacoes
            obs_normalizada = normalizar_texto(obs_original)
            
            if obs_original != obs_normalizada:
                problemas_encontrados.append({
                    'modelo': 'ComissaoPromocao',
                    'id': comissao.id,
                    'campo': 'observacoes',
                    'original': obs_original,
                    'normalizado': obs_normalizada
                })
    
    # Verificar FichaConceitoOficiais
    print("📋 Verificando FichaConceitoOficiais...")
    fichas_oficiais = FichaConceitoOficiais.objects.all()
    
    for ficha in fichas_oficiais:
        if ficha.observacoes:
            obs_original = ficha.observacoes
            obs_normalizada = normalizar_texto(obs_original)
            
            if obs_original != obs_normalizada:
                problemas_encontrados.append({
                    'modelo': 'FichaConceitoOficiais',
                    'id': ficha.id,
                    'campo': 'observacoes',
                    'original': obs_original,
                    'normalizado': obs_normalizada
                })
    
    # Verificar FichaConceitoPracas
    print("📋 Verificando FichaConceitoPracas...")
    fichas_pracas = FichaConceitoPracas.objects.all()
    
    for ficha in fichas_pracas:
        if ficha.observacoes:
            obs_original = ficha.observacoes
            obs_normalizada = normalizar_texto(obs_original)
            
            if obs_original != obs_normalizada:
                problemas_encontrados.append({
                    'modelo': 'FichaConceitoPracas',
                    'id': ficha.id,
                    'campo': 'observacoes',
                    'original': obs_original,
                    'normalizado': obs_normalizada
                })
    
    # Verificar SessaoComissao
    print("📋 Verificando SessaoComissao...")
    sessoes = SessaoComissao.objects.all()
    
    for sessao in sessoes:
        if sessao.observacoes:
            obs_original = sessao.observacoes
            obs_normalizada = normalizar_texto(obs_original)
            
            if obs_original != obs_normalizada:
                problemas_encontrados.append({
                    'modelo': 'SessaoComissao',
                    'id': sessao.id,
                    'campo': 'observacoes',
                    'original': obs_original,
                    'normalizado': obs_normalizada
                })
    
    # Verificar VotoDeliberacao
    print("📋 Verificando VotoDeliberacao...")
    votos = VotoDeliberacao.objects.all()
    
    for voto in votos:
        if voto.justificativa:
            just_original = voto.justificativa
            just_normalizada = normalizar_texto(just_original)
            
            if just_original != just_normalizada:
                problemas_encontrados.append({
                    'modelo': 'VotoDeliberacao',
                    'id': voto.id,
                    'campo': 'justificativa',
                    'original': just_original,
                    'normalizado': just_normalizada
                })
        
        if voto.voto_proferido:
            voto_original = voto.voto_proferido
            voto_normalizado = normalizar_texto(voto_original)
            
            if voto_original != voto_normalizado:
                problemas_encontrados.append({
                    'modelo': 'VotoDeliberacao',
                    'id': voto.id,
                    'campo': 'voto_proferido',
                    'original': voto_original,
                    'normalizado': voto_normalizado
                })
    
    # Verificar NotificacaoSessao
    print("📋 Verificando NotificacaoSessao...")
    notificacoes = NotificacaoSessao.objects.all()
    
    for notificacao in notificacoes:
        if notificacao.titulo:
            tit_original = notificacao.titulo
            tit_normalizado = normalizar_texto(tit_original)
            
            if tit_original != tit_normalizado:
                problemas_encontrados.append({
                    'modelo': 'NotificacaoSessao',
                    'id': notificacao.id,
                    'campo': 'titulo',
                    'original': tit_original,
                    'normalizado': tit_normalizado
                })
        
        if notificacao.mensagem:
            msg_original = notificacao.mensagem
            msg_normalizada = normalizar_texto(msg_original)
            
            if msg_original != msg_normalizada:
                problemas_encontrados.append({
                    'modelo': 'NotificacaoSessao',
                    'id': notificacao.id,
                    'campo': 'mensagem',
                    'original': msg_original,
                    'normalizado': msg_normalizada
                })
    
    # Verificar AlmanaqueMilitar
    print("📋 Verificando AlmanaqueMilitar...")
    almanaques = AlmanaqueMilitar.objects.all()
    
    for almanaque in almanaques:
        if almanaque.titulo:
            tit_original = almanaque.titulo
            tit_normalizado = normalizar_texto(tit_original)
            
            if tit_original != tit_normalizado:
                problemas_encontrados.append({
                    'modelo': 'AlmanaqueMilitar',
                    'id': almanaque.id,
                    'campo': 'titulo',
                    'original': tit_original,
                    'normalizado': tit_normalizado
                })
        
        if almanaque.observacoes:
            obs_original = almanaque.observacoes
            obs_normalizada = normalizar_texto(obs_original)
            
            if obs_original != obs_normalizada:
                problemas_encontrados.append({
                    'modelo': 'AlmanaqueMilitar',
                    'id': almanaque.id,
                    'campo': 'observacoes',
                    'original': obs_original,
                    'normalizado': obs_normalizada
                })
    
    # Verificar AssinaturaAlmanaque
    print("📋 Verificando AssinaturaAlmanaque...")
    assinaturas = AssinaturaAlmanaque.objects.all()
    
    for assinatura in assinaturas:
        if assinatura.cargo_funcao:
            cargo_original = assinatura.cargo_funcao
            cargo_normalizado = normalizar_texto(cargo_original)
            
            if cargo_original != cargo_normalizado:
                problemas_encontrados.append({
                    'modelo': 'AssinaturaAlmanaque',
                    'id': assinatura.id,
                    'campo': 'cargo_funcao',
                    'original': cargo_original,
                    'normalizado': cargo_normalizado
                })
        
        if assinatura.observacoes:
            obs_original = assinatura.observacoes
            obs_normalizada = normalizar_texto(obs_original)
            
            if obs_original != obs_normalizada:
                problemas_encontrados.append({
                    'modelo': 'AssinaturaAlmanaque',
                    'id': assinatura.id,
                    'campo': 'observacoes',
                    'original': obs_original,
                    'normalizado': obs_normalizada
                })
    
    return problemas_encontrados

if __name__ == '__main__':
    print("🔍 Verificação de Outros Campos para Normalização")
    print("=" * 60)
    
    # Verificar campos não normalizados
    problemas = verificar_campos_nao_normalizados()
    
    if problemas:
        print(f"\n⚠️  Encontrados {len(problemas)} campos que podem precisar de normalização:")
        
        # Agrupar por modelo
        por_modelo = {}
        for problema in problemas:
            modelo = problema['modelo']
            if modelo not in por_modelo:
                por_modelo[modelo] = []
            por_modelo[modelo].append(problema)
        
        for modelo, lista_problemas in por_modelo.items():
            print(f"\n📋 {modelo} ({len(lista_problemas)} campos):")
            for problema in lista_problemas[:5]:  # Mostrar apenas os primeiros 5
                print(f"  - ID {problema['id']} - {problema['campo']}:")
                print(f"    Original: {problema['original']}")
                print(f"    Normalizado: {problema['normalizado']}")
            
            if len(lista_problemas) > 5:
                print(f"  ... e mais {len(lista_problemas) - 5} campos")
        
        print(f"\n💡 Recomendação: Estes campos contêm caracteres especiais que podem causar problemas de exibição.")
        print("   Se desejar normalizar estes campos também, execute o script de normalização específico.")
    else:
        print("\n✅ Todos os campos verificados já estão normalizados!") 