# Correção de Arquivos Estáticos - Logo CBMEPI

## Problema Identificado
O arquivo `logo_cbmepi.png` não estava sendo servido corretamente, gerando erro 404:
```
WARNING 2025-07-30 11:42:04,178 log 108 129190530287424 Not Found: /static/logo_cbmepi.png
```

## Causa do Problema
O problema estava relacionado ao uso do `CompressedManifestStaticFilesStorage` do WhiteNoise, que requer um arquivo `staticfiles.json` para mapear os nomes dos arquivos originais para os nomes com hash. Como este arquivo não existia, os arquivos estáticos não eram servidos corretamente.

## Correções Aplicadas

### 1. Alteração do Storage de Arquivos Estáticos
Alterado de `CompressedManifestStaticFilesStorage` para `StaticFilesStorage` em todos os arquivos de configuração:

- `sepromcbmepi/settings_render.py`
- `sepromcbmepi/settings_supabase.py`
- `sepromcbmepi/settings_supabase_production.py`
- `sepromcbmepi/settings_aws_production.py`

**Antes:**
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Depois:**
```python
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
```

### 2. Adição do Middleware WhiteNoise
Adicionado o middleware do WhiteNoise no arquivo `sepromcbmepi/settings.py`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Adicionado
    "django.contrib.sessions.middleware.SessionMiddleware",
    # ... outros middlewares
]
```

### 3. Verificação dos Arquivos
Confirmado que o arquivo `logo_cbmepi.png` existe em:
- `static/logo_cbmepi.png` (74KB)
- `staticfiles/logo_cbmepi.png` (74KB)

### 4. Testes Realizados
- ✅ Arquivo existe no diretório `static/`
- ✅ Arquivo existe no diretório `staticfiles/`
- ✅ Arquivo sendo servido corretamente via HTTP local (status 200)
- ✅ Configurações de produção testadas e funcionando

## Resultado
Após as correções, o arquivo `logo_cbmepi.png` deve ser servido corretamente em todas as configurações (desenvolvimento e produção), eliminando os erros 404.

## Arquivos Modificados
1. `sepromcbmepi/settings.py` - Adicionado middleware WhiteNoise
2. `sepromcbmepi/settings_render.py` - Alterado storage
3. `sepromcbmepi/settings_supabase.py` - Alterado storage
4. `sepromcbmepi/settings_supabase_production.py` - Alterado storage
5. `sepromcbmepi/settings_aws_production.py` - Alterado storage

## Próximos Passos
1. Fazer commit das correções
2. Fazer deploy para produção
3. Verificar se o problema foi resolvido no ambiente de produção 