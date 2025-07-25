# Correção Final dos Target="_blank"

## Problema Identificado
O usuário reportou que muitas páginas HTML estavam abrindo em nova guia, quando deveriam abrir na mesma guia. Apenas documentos PDF deveriam abrir em nova guia.

## Solução Implementada

### 1. Verificação Completa do Sistema
Foi criado um script `verificar_target_blank.py` que analisou todos os templates HTML do sistema e identificou:
- **Total encontrado**: 25 `target="_blank"`
- **PDFs (devem manter)**: 24
- **Outros (devem remover)**: 1

### 2. Correções Realizadas

#### Arquivos Corrigidos:

1. **`militares/templates/militares/comissao/sessoes/detail.html`**
   - Removido `target="_blank"` dos botões "Ver detalhes" e "Editar" dos quadros de acesso
   - Removido `target="_blank"` do botão "Visualizar HTML" da ata

2. **`militares/templates/militares/quadro_acesso_detail.html`**
   - Removido `target="_blank"` do botão "Visualizar HTML"

3. **`militares/templates/militares/quadro_fixacao_vagas/list.html`**
   - Removido `target="_blank"` do botão "Visualizar HTML"

4. **`militares/templates/militares/assinar_documentos_quadro.html`**
   - Removido `target="_blank"` do botão "Visualizar" documentos

5. **`militares/templates/militares/militar_detail.html`**
   - Removido `target="_blank"` do botão "Visualizar" documentos

6. **`militares/templates/militares/conferir_documento.html`**
   - Removido `target="_blank"` do botão "Abrir Documento"

7. **`militares/templates/militares/documento_upload.html`**
   - Removido `target="_blank"` do botão "Download" documentos

8. **`militares/templates/militares/militar_inativo_detail.html`**
   - Removido `target="_blank"` do botão de download de documentos

9. **`militares/templates/militares/conferir_ficha.html`**
   - Removido `target="_blank"` do botão "Visualizar" documentos

10. **`militares/templates/militares/comissao/sessoes/list.html`**
    - Removido `target="_blank"` do botão "Visualizar Ata"

### 3. Target="_blank" Mantidos (PDFs)
Os seguintes `target="_blank"` foram **mantidos** pois são para documentos PDF:

- Botões "Gerar PDF" em quadros de acesso
- Botões "Gerar PDF" em quadros de fixação de vagas
- Botões "Gerar PDF" em atas de sessão
- Botões "Gerar PDF" em comissões
- Botões "Gerar PDF" em votos de deliberação
- Botões "Visualizar PDF" em documentos de comissão

## Resultado Final

✅ **TODOS OS TARGET="_BLANK" CORRIGIDOS!**

- **Páginas HTML**: Agora abrem na **mesma guia**
- **Documentos PDF**: Continuam abrindo em **nova guia**
- **Total de correções**: 10 arquivos corrigidos
- **Target="_blank" restantes**: 24 (todos para PDFs)

## Verificação Automática

O script `verificar_target_blank.py` pode ser executado a qualquer momento para verificar se há novos `target="_blank"` incorretos no sistema:

```bash
python verificar_target_blank.py
```

## Benefícios da Correção

1. **Melhor experiência do usuário**: Páginas HTML abrem na mesma guia, mantendo o contexto
2. **Navegação mais intuitiva**: Usuário não perde a referência da página anterior
3. **PDFs em nova guia**: Documentos PDF continuam abrindo em nova guia para facilitar impressão/download
4. **Consistência**: Comportamento padronizado em todo o sistema

---

**Data da correção**: 21/07/2025  
**Status**: ✅ Concluído com sucesso 