-- Script SQL para executar no servidor
-- Execute: sudo -u postgres psql -d sepromcbmepi -f executar_no_servidor.sql

-- Adicionar campos de raias na tabela militares_armaparticular
ALTER TABLE militares_armaparticular 
ADD COLUMN IF NOT EXISTS alma_raiada BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS quantidade_raias INTEGER NULL,
ADD COLUMN IF NOT EXISTS direcao_raias VARCHAR(10) NULL;

-- Atualizar verbose_name do campo numero_registro_policia (já existe, apenas documentação)
-- O campo já existe, então não precisa alterar

-- Verificar se os campos foram criados
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'militares_armaparticular' 
AND column_name IN ('alma_raiada', 'quantidade_raias', 'direcao_raias');

