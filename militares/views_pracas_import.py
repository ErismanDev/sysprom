# Importar todas as views de praças
from .views_pracas import (
    ficha_conceito_pracas_list,
    gerar_fichas_conceito_pracas_todos,
    limpar_pontos_fichas_conceito_pracas,
    quadro_acesso_pracas_detail,
    quadro_acesso_pracas_edit,
    quadro_acesso_pracas_pdf,
    quadro_acesso_pracas_print,
    gerar_quadro_acesso_pracas,
    regerar_quadro_acesso_pracas,
    delete_quadro_acesso_pracas,
    homologar_quadro_acesso_pracas,
    deshomologar_quadro_acesso_pracas,
    elaborar_quadro_acesso_pracas,
    marcar_nao_elaborado_pracas,
    relatorio_requisitos_quadro_pracas,
    # Views de quadros de fixação de vagas para praças removidas - redundantes
    regras_requisitos_pracas,
) 