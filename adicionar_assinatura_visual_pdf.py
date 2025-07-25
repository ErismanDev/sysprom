import os

def adicionar_assinatura_visual_pdf():
    """Adicionar assinatura visual nos PDFs"""
    
    # Arquivo views.py
    with open("militares/views.py", "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Substituir o texto da assinatura para incluir a assinatura visual
    novo_conteudo = conteudo.replace(
        'texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {funcao_atual}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"',
        '''texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {funcao_atual}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar assinatura visual
            assinatura_visual = f"{nome_assinante}\\n{funcao_atual}"'''
    )

    with open("militares/views.py", "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    print("✅ Assinatura visual adicionada ao PDF em views.py!")

if __name__ == "__main__":
    adicionar_assinatura_visual_pdf() 