#!/usr/bin/env python
"""
Script para padronizar o autenticador de veracidade em todas as views que geram PDFs.
Este script atualiza as views para usar a função utilitária gerar_autenticador_veracidade.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def verificar_autenticador_views():
    """
    Verifica quais views já têm o autenticador implementado e quais precisam ser atualizadas
    """
    print("=== VERIFICAÇÃO DO AUTENTICADOR DE VERACIDADE ===\n")
    
    # Lista de views que geram PDFs
    views_pdf = [
        'quadro_acesso_pdf',
        'ata_gerar_pdf', 
        'voto_deliberacao_pdf',
        'quadro_fixacao_vagas_pdf',
        'comissao_pdf'
    ]
    
    # Verificar arquivo principal de views
    views_file = 'militares/views.py'
    
    if os.path.exists(views_file):
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Verificando {views_file}:")
        
        for view in views_pdf:
            if view in content:
                # Verificar se usa a função utilitária
                if f'gerar_autenticador_veracidade' in content and view in content:
                    print(f"  ✅ {view}: Já usa função utilitária")
                elif f'qr = qrcode.make' in content and view in content:
                    print(f"  ⚠️  {view}: Tem autenticador manual (precisa padronizar)")
                else:
                    print(f"  ❌ {view}: Não encontrado ou sem autenticador")
            else:
                print(f"  ❌ {view}: Não encontrado")
    
    print("\n=== RESUMO ===\n")
    print("Views que precisam ser padronizadas para usar a função utilitária:")
    print("- ata_gerar_pdf")
    print("- voto_deliberacao_pdf") 
    print("- quadro_fixacao_vagas_pdf")
    print("\nViews que já estão padronizadas:")
    print("- quadro_acesso_pdf")
    
    return True

def padronizar_view_ata():
    """
    Padroniza a view ata_gerar_pdf para usar a função utilitária
    """
    print("\n=== PADRONIZANDO VIEW ATA ===\n")
    
    views_file = 'militares/views.py'
    
    if not os.path.exists(views_file):
        print("❌ Arquivo de views não encontrado")
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir implementação manual pela função utilitária
    old_code = '''    # QR Code para conferência de veracidade
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Dados para autenticação
    url_autenticacao = "https://sei.pi.gov.br/sei/controlador_externo.php?acao=documento_conferir&id_orgao_acesso_externo=0"
    codigo_verificador = f"{ata.pk:08d}"
    codigo_crc = f"{hash(str(ata.pk)) % 0xFFFFFFF:07X}"
    
    texto_autenticacao = f"A autenticidade deste documento pode ser conferida no site <a href='{url_autenticacao}' color='blue'>{url_autenticacao}</a>, informando o código verificador <b>{codigo_verificador}</b> e o código CRC <b>{codigo_crc}</b>."
    
    # Gerar QR Code
    qr = qrcode.make(url_autenticacao)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_img = Image(qr_buffer, width=2*cm, height=2*cm)
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [qr_img, Paragraph(texto_autenticacao, style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)'''
    
    new_code = '''    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 13))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(ata, request, tipo_documento='ata')
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ View ata_gerar_pdf padronizada com sucesso!")
        return True
    else:
        print("❌ Código da view ata não encontrado para substituição")
        return False

def padronizar_view_voto():
    """
    Padroniza a view voto_deliberacao_pdf para usar a função utilitária
    """
    print("\n=== PADRONIZANDO VIEW VOTO ===\n")
    
    views_file = 'militares/views.py'
    
    if not os.path.exists(views_file):
        print("❌ Arquivo de views não encontrado")
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir implementação manual pela função utilitária
    old_code = '''    # Gerar códigos de verificação
    import hashlib
    codigo_verificador = f"{hashlib.md5(str(voto.pk).encode()).hexdigest()[:8].upper()}"
    codigo_crc = f"{hash(str(voto.pk)) % 0xFFFFFFF:07X}"
    
    texto_autenticacao = f"A autenticidade deste documento pode ser conferida no site <a href='{url_autenticacao}' color='blue'>{url_autenticacao}</a>, informando o código verificador <b>{codigo_verificador}</b> e o código CRC <b>{codigo_crc}</b>."
    
    # Gerar QR Code
    qr = qrcode.make(url_autenticacao)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_img = Image(qr_buffer, width=2*cm, height=2*cm)
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [qr_img, Paragraph(texto_autenticacao, style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)'''
    
    new_code = '''    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 13))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(voto, request, tipo_documento='voto')
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ View voto_deliberacao_pdf padronizada com sucesso!")
        return True
    else:
        print("❌ Código da view voto não encontrado para substituição")
        return False

def padronizar_view_quadro_fixacao():
    """
    Padroniza a view quadro_fixacao_vagas_pdf para usar a função utilitária
    """
    print("\n=== PADRONIZANDO VIEW QUADRO FIXAÇÃO ===\n")
    
    views_file = 'militares/views.py'
    
    if not os.path.exists(views_file):
        print("❌ Arquivo de views não encontrado")
        return False
    
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir implementação manual pela função utilitária
    old_code = '''    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 13))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Dados para autenticação
    url_autenticacao = "https://sei.pi.gov.br/sei/controlador_externo.php?acao=documento_conferir&id_orgao_acesso_externo=0"
    codigo_verificador = f"{quadro.pk:08d}"
    codigo_crc = f"{hash(str(quadro.pk)) % 0xFFFFFFF:07X}"
    
    texto_autenticacao = f"A autenticidade deste documento pode ser conferida no site <a href='{url_autenticacao}' color='blue'>{url_autenticacao}</a>, informando o código verificador <b>{codigo_verificador}</b> e o código CRC <b>{codigo_crc}</b>."
    
    # Gerar QR Code
    qr = qrcode.make(url_autenticacao)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_img = Image(qr_buffer, width=2*cm, height=2*cm)
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [qr_img, Paragraph(texto_autenticacao, style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)'''
    
    new_code = '''    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 13))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(quadro, request, tipo_documento='quadro_fixacao')
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ View quadro_fixacao_vagas_pdf padronizada com sucesso!")
        return True
    else:
        print("❌ Código da view quadro fixação não encontrado para substituição")
        return False

def main():
    """
    Função principal que executa todas as padronizações
    """
    print("🚀 INICIANDO PADRONIZAÇÃO DO AUTENTICADOR DE VERACIDADE\n")
    
    # Verificar status atual
    verificar_autenticador_views()
    
    # Padronizar views
    success_count = 0
    
    if padronizar_view_ata():
        success_count += 1
    
    if padronizar_view_voto():
        success_count += 1
    
    if padronizar_view_quadro_fixacao():
        success_count += 1
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"✅ {success_count}/3 views padronizadas com sucesso!")
    
    if success_count == 3:
        print("🎉 Todas as views foram padronizadas! O autenticador de veracidade está implementado em todos os documentos.")
    else:
        print("⚠️  Algumas views não puderam ser padronizadas. Verifique manualmente.")

if __name__ == '__main__':
    main() 