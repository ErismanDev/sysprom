#!/usr/bin/env python
"""
Script simplificado para corrigir problemas de codificação no banco de dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import connection
from militares.models import *

def verificar_caracteres_problematicos():
    """
    Verifica caracteres problemáticos usando Django ORM
    """
    print("🔍 Verificando caracteres problemáticos no banco de dados...")
    
    problemas_encontrados = []
    
    # Verificar na tabela Militar
    print("\n📋 Verificando tabela: Militar")
    militares = Militar.objects.all()
    
    for militar in militares:
        campos_problematicos = []
        
        # Verificar nome_completo
        if militar.nome_completo:
            if any(char in militar.nome_completo for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
                campos_problematicos.append(f"nome_completo: {militar.nome_completo}")
        
        # Verificar nome_guerra
        if militar.nome_guerra:
            if any(char in militar.nome_guerra for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
                campos_problematicos.append(f"nome_guerra: {militar.nome_guerra}")
        
        # Verificar observacoes
        if militar.observacoes:
            if any(char in militar.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
                campos_problematicos.append(f"observacoes: {militar.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'Militar',
                'id': militar.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela CargoComissao
    print("📋 Verificando tabela: CargoComissao")
    cargos = CargoComissao.objects.all()
    
    for cargo in cargos:
        campos_problematicos = []
        
        if cargo.nome and any(char in cargo.nome for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"nome: {cargo.nome}")
        
        if cargo.descricao and any(char in cargo.descricao for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"descricao: {cargo.descricao}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'CargoComissao',
                'id': cargo.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela FichaConceitoOficiais
    print("📋 Verificando tabela: FichaConceitoOficiais")
    fichas_oficiais = FichaConceitoOficiais.objects.all()
    
    for ficha in fichas_oficiais:
        campos_problematicos = []
        
        if ficha.observacoes and any(char in ficha.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"observacoes: {ficha.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'FichaConceitoOficiais',
                'id': ficha.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela FichaConceitoPracas
    print("📋 Verificando tabela: FichaConceitoPracas")
    fichas_pracas = FichaConceitoPracas.objects.all()
    
    for ficha in fichas_pracas:
        campos_problematicos = []
        
        if ficha.observacoes and any(char in ficha.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"observacoes: {ficha.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'FichaConceitoPracas',
                'id': ficha.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela SessaoComissao
    print("📋 Verificando tabela: SessaoComissao")
    sessoes = SessaoComissao.objects.all()
    
    for sessao in sessoes:
        campos_problematicos = []
        
        if sessao.observacoes and any(char in sessao.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"observacoes: {sessao.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'SessaoComissao',
                'id': sessao.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela ComissaoPromocao
    print("📋 Verificando tabela: ComissaoPromocao")
    comissoes = ComissaoPromocao.objects.all()
    
    for comissao in comissoes:
        campos_problematicos = []
        
        if comissao.nome and any(char in comissao.nome for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"nome: {comissao.nome}")
        
        if comissao.observacoes and any(char in comissao.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"observacoes: {comissao.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'ComissaoPromocao',
                'id': comissao.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela VotoDeliberacao
    print("📋 Verificando tabela: VotoDeliberacao")
    votos = VotoDeliberacao.objects.all()
    
    for voto in votos:
        campos_problematicos = []
        
        if voto.justificativa and any(char in voto.justificativa for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"justificativa: {voto.justificativa}")
        
        if voto.voto_proferido and any(char in voto.voto_proferido for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"voto_proferido: {voto.voto_proferido}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'VotoDeliberacao',
                'id': voto.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela NotificacaoSessao
    print("📋 Verificando tabela: NotificacaoSessao")
    notificacoes = NotificacaoSessao.objects.all()
    
    for notificacao in notificacoes:
        campos_problematicos = []
        
        if notificacao.titulo and any(char in notificacao.titulo for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"titulo: {notificacao.titulo}")
        
        if notificacao.mensagem and any(char in notificacao.mensagem for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"mensagem: {notificacao.mensagem}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'NotificacaoSessao',
                'id': notificacao.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela AlmanaqueMilitar
    print("📋 Verificando tabela: AlmanaqueMilitar")
    almanaques = AlmanaqueMilitar.objects.all()
    
    for almanaque in almanaques:
        campos_problematicos = []
        
        if almanaque.titulo and any(char in almanaque.titulo for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"titulo: {almanaque.titulo}")
        
        if almanaque.observacoes and any(char in almanaque.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"observacoes: {almanaque.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'AlmanaqueMilitar',
                'id': almanaque.id,
                'campos': campos_problematicos
            })
    
    # Verificar na tabela AssinaturaAlmanaque
    print("📋 Verificando tabela: AssinaturaAlmanaque")
    assinaturas = AssinaturaAlmanaque.objects.all()
    
    for assinatura in assinaturas:
        campos_problematicos = []
        
        if assinatura.cargo_funcao and any(char in assinatura.cargo_funcao for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"cargo_funcao: {assinatura.cargo_funcao}")
        
        if assinatura.observacoes and any(char in assinatura.observacoes for char in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ'):
            campos_problematicos.append(f"observacoes: {assinatura.observacoes}")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'modelo': 'AssinaturaAlmanaque',
                'id': assinatura.id,
                'campos': campos_problematicos
            })
    
    return problemas_encontrados

def corrigir_caracteres_banco():
    """
    Corrige caracteres problemáticos no banco de dados
    """
    print("🔧 Corrigindo caracteres problemáticos no banco de dados...")
    
    # Mapeamento de caracteres problemáticos
    substituicoes = {
        'à': 'à',
        'á': 'á', 
        'â': 'â',
        'ã': 'ã',
        'ä': 'ä',
        'å': 'å',
        'ç': 'ç',
        'è': 'è',
        'é': 'é',
        'ê': 'ê',
        'ë': 'ë',
        'ì': 'ì',
        'í': 'í',
        'î': 'î',
        'ï': 'ï',
        'ñ': 'ñ',
        'ò': 'ò',
        'ó': 'ó',
        'ô': 'ô',
        'õ': 'õ',
        'ö': 'ö',
        'ù': 'ù',
        'ú': 'ú',
        'û': 'û',
        'ü': 'ü',
        'ý': 'ý',
        'ÿ': 'ÿ',
        'À': 'À',
        'Á': 'Á',
        'Â': 'Â',
        'Ã': 'Ã',
        'Ä': 'Ä',
        'Ç': 'Ç',
        'È': 'È',
        'É': 'É',
        'Ê': 'Ê',
        'Ë': 'Ë',
        'Ì': 'Ì',
        'Í': 'Í',
        'Î': 'Î',
        'Ï': 'Ï',
        'Ñ': 'Ñ',
        'Ò': 'Ò',
        'Ó': 'Ó',
        'Ô': 'Ô',
        'Õ': 'Õ',
        'Ö': 'Ö',
        'Ù': 'Ù',
        'Ú': 'Ú',
        'Û': 'Û',
        'Ü': 'Ü',
        'Ý': 'Ý',
    }
    
    total_corrigidos = 0
    
    # Corrigir Militar
    print("\n📋 Corrigindo tabela: Militar")
    militares = Militar.objects.all()
    
    for militar in militares:
        alterado = False
        
        if militar.nome_completo:
            nome_original = militar.nome_completo
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    militar.nome_completo = militar.nome_completo.replace(char_antigo, char_novo)
            if militar.nome_completo != nome_original:
                alterado = True
        
        if militar.nome_guerra:
            nome_original = militar.nome_guerra
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    militar.nome_guerra = militar.nome_guerra.replace(char_antigo, char_novo)
            if militar.nome_guerra != nome_original:
                alterado = True
        
        if militar.observacoes:
            obs_original = militar.observacoes
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    militar.observacoes = militar.observacoes.replace(char_antigo, char_novo)
            if militar.observacoes != obs_original:
                alterado = True
        
        if alterado:
            militar.save()
            total_corrigidos += 1
            print(f"  ✅ Militar ID {militar.id} corrigido")
    
    # Corrigir Cargo
    print("📋 Corrigindo tabela: Cargo")
    cargos = Cargo.objects.all()
    
    for cargo in cargos:
        alterado = False
        
        if cargo.nome:
            nome_original = cargo.nome
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    cargo.nome = cargo.nome.replace(char_antigo, char_novo)
            if cargo.nome != nome_original:
                alterado = True
        
        if cargo.descricao:
            desc_original = cargo.descricao
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    cargo.descricao = cargo.descricao.replace(char_antigo, char_novo)
            if cargo.descricao != desc_original:
                alterado = True
        
        if alterado:
            cargo.save()
            total_corrigidos += 1
            print(f"  ✅ Cargo ID {cargo.id} corrigido")
    
    # Corrigir Funcao
    print("📋 Corrigindo tabela: Funcao")
    funcoes = Funcao.objects.all()
    
    for funcao in funcoes:
        alterado = False
        
        if funcao.nome:
            nome_original = funcao.nome
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    funcao.nome = funcao.nome.replace(char_antigo, char_novo)
            if funcao.nome != nome_original:
                alterado = True
        
        if funcao.descricao:
            desc_original = funcao.descricao
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    funcao.descricao = funcao.descricao.replace(char_antigo, char_novo)
            if funcao.descricao != desc_original:
                alterado = True
        
        if alterado:
            funcao.save()
            total_corrigidos += 1
            print(f"  ✅ Funcao ID {funcao.id} corrigido")
    
    # Corrigir Quadro
    print("📋 Corrigindo tabela: Quadro")
    quadros = Quadro.objects.all()
    
    for quadro in quadros:
        alterado = False
        
        if quadro.nome:
            nome_original = quadro.nome
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    quadro.nome = quadro.nome.replace(char_antigo, char_novo)
            if quadro.nome != nome_original:
                alterado = True
        
        if quadro.descricao:
            desc_original = quadro.descricao
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    quadro.descricao = quadro.descricao.replace(char_antigo, char_novo)
            if quadro.descricao != desc_original:
                alterado = True
        
        if alterado:
            quadro.save()
            total_corrigidos += 1
            print(f"  ✅ Quadro ID {quadro.id} corrigido")
    
    # Corrigir FichaConceito
    print("📋 Corrigindo tabela: FichaConceito")
    fichas = FichaConceito.objects.all()
    
    for ficha in fichas:
        alterado = False
        
        if ficha.observacoes:
            obs_original = ficha.observacoes
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    ficha.observacoes = ficha.observacoes.replace(char_antigo, char_novo)
            if ficha.observacoes != obs_original:
                alterado = True
        
        if ficha.parecer:
            par_original = ficha.parecer
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    ficha.parecer = ficha.parecer.replace(char_antigo, char_novo)
            if ficha.parecer != par_original:
                alterado = True
        
        if alterado:
            ficha.save()
            total_corrigidos += 1
            print(f"  ✅ FichaConceito ID {ficha.id} corrigido")
    
    # Corrigir Sessao
    print("📋 Corrigindo tabela: Sessao")
    sessoes = Sessao.objects.all()
    
    for sessao in sessoes:
        alterado = False
        
        if sessao.observacoes:
            obs_original = sessao.observacoes
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    sessao.observacoes = sessao.observacoes.replace(char_antigo, char_novo)
            if sessao.observacoes != obs_original:
                alterado = True
        
        if alterado:
            sessao.save()
            total_corrigidos += 1
            print(f"  ✅ Sessao ID {sessao.id} corrigido")
    
    # Corrigir Comissao
    print("📋 Corrigindo tabela: Comissao")
    comissoes = Comissao.objects.all()
    
    for comissao in comissoes:
        alterado = False
        
        if comissao.nome:
            nome_original = comissao.nome
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    comissao.nome = comissao.nome.replace(char_antigo, char_novo)
            if comissao.nome != nome_original:
                alterado = True
        
        if comissao.observacoes:
            obs_original = comissao.observacoes
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    comissao.observacoes = comissao.observacoes.replace(char_antigo, char_novo)
            if comissao.observacoes != obs_original:
                alterado = True
        
        if alterado:
            comissao.save()
            total_corrigidos += 1
            print(f"  ✅ Comissao ID {comissao.id} corrigido")
    
    # Corrigir Voto
    print("📋 Corrigindo tabela: Voto")
    votos = Voto.objects.all()
    
    for voto in votos:
        alterado = False
        
        if voto.justificativa:
            just_original = voto.justificativa
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    voto.justificativa = voto.justificativa.replace(char_antigo, char_novo)
            if voto.justificativa != just_original:
                alterado = True
        
        if voto.voto_proferido:
            voto_original = voto.voto_proferido
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    voto.voto_proferido = voto.voto_proferido.replace(char_antigo, char_novo)
            if voto.voto_proferido != voto_original:
                alterado = True
        
        if alterado:
            voto.save()
            total_corrigidos += 1
            print(f"  ✅ Voto ID {voto.id} corrigido")
    
    # Corrigir Notificacao
    print("📋 Corrigindo tabela: Notificacao")
    notificacoes = Notificacao.objects.all()
    
    for notificacao in notificacoes:
        alterado = False
        
        if notificacao.titulo:
            tit_original = notificacao.titulo
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    notificacao.titulo = notificacao.titulo.replace(char_antigo, char_novo)
            if notificacao.titulo != tit_original:
                alterado = True
        
        if notificacao.mensagem:
            msg_original = notificacao.mensagem
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    notificacao.mensagem = notificacao.mensagem.replace(char_antigo, char_novo)
            if notificacao.mensagem != msg_original:
                alterado = True
        
        if alterado:
            notificacao.save()
            total_corrigidos += 1
            print(f"  ✅ Notificacao ID {notificacao.id} corrigido")
    
    # Corrigir Almanaque
    print("📋 Corrigindo tabela: Almanaque")
    almanaques = Almanaque.objects.all()
    
    for almanaque in almanaques:
        alterado = False
        
        if almanaque.titulo:
            tit_original = almanaque.titulo
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    almanaque.titulo = almanaque.titulo.replace(char_antigo, char_novo)
            if almanaque.titulo != tit_original:
                alterado = True
        
        if almanaque.observacoes:
            obs_original = almanaque.observacoes
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    almanaque.observacoes = almanaque.observacoes.replace(char_antigo, char_novo)
            if almanaque.observacoes != obs_original:
                alterado = True
        
        if alterado:
            almanaque.save()
            total_corrigidos += 1
            print(f"  ✅ Almanaque ID {almanaque.id} corrigido")
    
    # Corrigir AlmanaqueAssinatura
    print("📋 Corrigindo tabela: AlmanaqueAssinatura")
    assinaturas = AlmanaqueAssinatura.objects.all()
    
    for assinatura in assinaturas:
        alterado = False
        
        if assinatura.cargo_funcao:
            cargo_original = assinatura.cargo_funcao
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    assinatura.cargo_funcao = assinatura.cargo_funcao.replace(char_antigo, char_novo)
            if assinatura.cargo_funcao != cargo_original:
                alterado = True
        
        if assinatura.observacoes:
            obs_original = assinatura.observacoes
            for char_antigo, char_novo in substituicoes.items():
                if char_antigo != char_novo:
                    assinatura.observacoes = assinatura.observacoes.replace(char_antigo, char_novo)
            if assinatura.observacoes != obs_original:
                alterado = True
        
        if alterado:
            assinatura.save()
            total_corrigidos += 1
            print(f"  ✅ AlmanaqueAssinatura ID {assinatura.id} corrigido")
    
    print(f"\n📊 Total de registros corrigidos: {total_corrigidos}")
    return total_corrigidos

if __name__ == '__main__':
    print("🔧 Script Simplificado de Correção de Caracteres no Banco de Dados")
    print("=" * 70)
    
    # Verificar caracteres problemáticos
    problemas = verificar_caracteres_problematicos()
    
    if problemas:
        print(f"\n⚠️  Encontrados {len(problemas)} problemas de caracteres:")
        for problema in problemas:
            print(f"  - {problema['modelo']} ID {problema['id']}: {', '.join(problema['campos'])}")
        
        # Perguntar se deve corrigir
        resposta = input("\nDeseja corrigir os problemas de caracteres? (s/n): ").lower()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            # Corrigir caracteres
            total_corrigidos = corrigir_caracteres_banco()
            print(f"\n✅ Correção concluída! {total_corrigidos} registros corrigidos.")
        else:
            print("\n❌ Operação cancelada pelo usuário.")
    else:
        print("\n✅ Nenhum problema de caracteres encontrado no banco de dados!") 