#!/usr/bin/env python
"""
Script para recriar completamente o template de detalhes
"""

def recriar_template_detalhes():
    """Recria completamente o template de detalhes"""
    
    print("🔧 RECRIANDO TEMPLATE DE DETALHES")
    print("=" * 60)
    
    # Template completo com todos os módulos
    template_content = '''{% extends 'base.html' %}
{% load static %}

{% block title %}Detalhes do Cargo/Função{% endblock %}

{% block extra_css %}
<style>
    /* Filtros discretos */
    .filters-discreet {
        margin-top: 15px;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        opacity: 0.7;
        transition: opacity 0.3s ease;
    }
    
    .filters-discreet:hover {
        opacity: 1;
    }
    
    .filter-select-discreet {
        padding: 6px 12px;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        font-size: 12px;
        background: white;
        color: #495057;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .filter-select-discreet:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Estilos para permissões */
    .permissao-card {
        transition: all 0.3s ease;
        border: 2px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .permissao-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .permissao-badge {
        font-size: 0.75rem;
        padding: 0.4rem 0.6rem;
        margin: 0.2rem;
        border-radius: 15px;
        display: inline-block;
        font-weight: 500;
    }
    
    .permissao-visualizar { background-color: #e3f2fd; color: #1976d2; border: 1px solid #bbdefb; }
    .permissao-criar { background-color: #e8f5e8; color: #2e7d32; border: 1px solid #c8e6c9; }
    .permissao-editar { background-color: #fff3e0; color: #f57c00; border: 1px solid #ffcc02; }
    .permissao-excluir { background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }
    .permissao-aprovar { background-color: #f3e5f5; color: #7b1fa2; border: 1px solid #e1bee7; }
    .permissao-homologar { background-color: #e0f2f1; color: #00695c; border: 1px solid #b2dfdb; }
    .permissao-gerar-pdf { background-color: #fff8e1; color: #f9a825; border: 1px solid #ffecb3; }
    .permissao-imprimir { background-color: #f1f8e9; color: #558b2f; border: 1px solid #dcedc8; }
    .permissao-assinar { background-color: #e8eaf6; color: #3949ab; border: 1px solid #c5cae9; }
    .permissao-administrar { background-color: #fce4ec; color: #c2185b; border: 1px solid #f8bbd9; }
    
    .modulo-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    
    .modulo-stats {
        font-size: 0.8rem;
        color: #6c757d;
        margin-left: 0.5rem;
    }
    
    .permissao-count {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #dc3545;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Responsivo */
    @media (max-width: 768px) {
        .filters-discreet {
            flex-direction: column;
        }
        
        .permissao-badge {
            font-size: 0.7rem;
            padding: 0.3rem 0.5rem;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8">
            <div class="card mb-4">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0"><i class="fas fa-users-cog"></i> {{ cargo.nome }}</h4>
                </div>
                <div class="card-body">
                    <dl class="row">
                        <dt class="col-sm-4">Nome</dt>
                        <dd class="col-sm-8">{{ cargo.nome }}</dd>
                        <dt class="col-sm-4">Descrição</dt>
                        <dd class="col-sm-8">{{ cargo.descricao|default:'-' }}</dd>
                        <dt class="col-sm-4">Ativo</dt>
                        <dd class="col-sm-8">{% if cargo.ativo %}<span class="badge bg-success">Sim</span>{% else %}<span class="badge bg-danger">Não</span>{% endif %}</dd>
                        <dt class="col-sm-4">Ordem</dt>
                        <dd class="col-sm-8">{{ cargo.ordem }}</dd>
                    </dl>
                    <div class="d-flex justify-content-end">
                        <a href="{% url 'militares:cargo_funcao_update' cargo.id %}" class="btn btn-primary me-2">
                            <i class="fas fa-edit"></i> Editar
                        </a>
                        
                        <a href="{% url 'militares:cargo_funcao_delete' cargo.id %}" class="btn btn-danger me-2">
                            <i class="fas fa-trash"></i> Excluir
                        </a>

                        <a href="{% url 'militares:cargo_funcao_list' %}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i> Voltar
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Coluna de Estatísticas -->
        <div class="col-md-4">
            <div class="card mb-4">
                <div class="card-header bg-light">
                    <h5 class="mb-0"><i class="fas fa-chart-pie"></i> Estatísticas</h5>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-6">
                            <div class="border-end">
                                <h4 class="text-primary">{{ permissoes_count }}</h4>
                                <small class="text-muted">Permissões</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <h4 class="text-success">{{ usuarios_count }}</h4>
                            <small class="text-muted">Usuários</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Seção de Permissões -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="fas fa-shield-alt"></i> Permissões do Sistema</h5>
                    <div>
                        <span class="badge bg-light text-dark">{{ permissoes_count }} permissões</span>
                    </div>
                </div>
                <div class="card-body">
                    {% if permissoes_por_modulo %}
                        <div class="row">
                            {% for modulo, permissoes in permissoes_por_modulo.items %}
                            <div class="col-md-6 col-lg-4 mb-4">
                                <div class="card permissao-card position-relative">
                                    <div class="card-header bg-light">
                                        <h6 class="mb-0">
                                            {% if modulo == 'MILITARES' %}
                                                <i class="fas fa-users modulo-icon"></i>
                                            {% elif modulo == 'FICHAS_CONCEITO' %}
                                                <i class="fas fa-file-alt modulo-icon"></i>
                                            {% elif modulo == 'QUADROS_ACESSO' %}
                                                <i class="fas fa-table modulo-icon"></i>
                                            {% elif modulo == 'PROMOCOES' %}
                                                <i class="fas fa-star modulo-icon"></i>
                                            {% elif modulo == 'VAGAS' %}
                                                <i class="fas fa-chair modulo-icon"></i>
                                            {% elif modulo == 'COMISSAO' %}
                                                <i class="fas fa-gavel modulo-icon"></i>
                                            {% elif modulo == 'DOCUMENTOS' %}
                                                <i class="fas fa-file-pdf modulo-icon"></i>
                                            {% elif modulo == 'USUARIOS' %}
                                                <i class="fas fa-user-cog modulo-icon"></i>
                                            {% elif modulo == 'RELATORIOS' %}
                                                <i class="fas fa-chart-bar modulo-icon"></i>
                                            {% elif modulo == 'CONFIGURACOES' %}
                                                <i class="fas fa-cogs modulo-icon"></i>
                                            {% elif modulo == 'ALMANAQUES' %}
                                                <i class="fas fa-book modulo-icon"></i>
                                            {% elif modulo == 'CALENDARIOS' %}
                                                <i class="fas fa-calendar-alt modulo-icon"></i>
                                            {% elif modulo == 'NOTIFICACOES' %}
                                                <i class="fas fa-bell modulo-icon"></i>
                                            {% elif modulo == 'MODELOS_ATA' %}
                                                <i class="fas fa-file-contract modulo-icon"></i>
                                            {% elif modulo == 'CARGOS_COMISSAO' %}
                                                <i class="fas fa-user-tie modulo-icon"></i>
                                            {% elif modulo == 'QUADROS_FIXACAO' %}
                                                <i class="fas fa-thumbtack modulo-icon"></i>
                                            {% elif modulo == 'ASSINATURAS' %}
                                                <i class="fas fa-signature modulo-icon"></i>
                                            {% elif modulo == 'ESTATISTICAS' %}
                                                <i class="fas fa-chart-line modulo-icon"></i>
                                            {% elif modulo == 'EXPORTACAO' %}
                                                <i class="fas fa-download modulo-icon"></i>
                                            {% elif modulo == 'IMPORTACAO' %}
                                                <i class="fas fa-upload modulo-icon"></i>
                                            {% elif modulo == 'BACKUP' %}
                                                <i class="fas fa-database modulo-icon"></i>
                                            {% elif modulo == 'AUDITORIA' %}
                                                <i class="fas fa-clipboard-list modulo-icon"></i>
                                            {% elif modulo == 'DASHBOARD' %}
                                                <i class="fas fa-tachometer-alt modulo-icon"></i>
                                            {% elif modulo == 'BUSCA' %}
                                                <i class="fas fa-search modulo-icon"></i>
                                            {% elif modulo == 'AJAX' %}
                                                <i class="fas fa-sync-alt modulo-icon"></i>
                                            {% elif modulo == 'API' %}
                                                <i class="fas fa-code modulo-icon"></i>
                                            {% elif modulo == 'SESSAO' %}
                                                <i class="fas fa-clock modulo-icon"></i>
                                            {% elif modulo == 'FUNCAO' %}
                                                <i class="fas fa-user-tag modulo-icon"></i>
                                            {% elif modulo == 'PERFIL' %}
                                                <i class="fas fa-id-card modulo-icon"></i>
                                            {% elif modulo == 'SISTEMA' %}
                                                <i class="fas fa-server modulo-icon"></i>
                                            {% else %}
                                                <i class="fas fa-cube modulo-icon"></i>
                                            {% endif %}
                                            {{ modulo|title }}
                                            <span class="modulo-stats">({{ permissoes|length }})</span>
                                        </h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="d-flex flex-wrap">
                                            {% for permissao in permissoes %}
                                            <span class="permissao-badge permissao-{{ permissao.acesso|lower|cut:'_' }}">
                                                {% if permissao.acesso == 'VISUALIZAR' %}
                                                    <i class="fas fa-eye"></i>
                                                {% elif permissao.acesso == 'CRIAR' %}
                                                    <i class="fas fa-plus"></i>
                                                {% elif permissao.acesso == 'EDITAR' %}
                                                    <i class="fas fa-edit"></i>
                                                {% elif permissao.acesso == 'EXCLUIR' %}
                                                    <i class="fas fa-trash"></i>
                                                {% elif permissao.acesso == 'APROVAR' %}
                                                    <i class="fas fa-check"></i>
                                                {% elif permissao.acesso == 'HOMOLOGAR' %}
                                                    <i class="fas fa-stamp"></i>
                                                {% elif permissao.acesso == 'GERAR_PDF' %}
                                                    <i class="fas fa-file-pdf"></i>
                                                {% elif permissao.acesso == 'IMPRIMIR' %}
                                                    <i class="fas fa-print"></i>
                                                {% elif permissao.acesso == 'ASSINAR' %}
                                                    <i class="fas fa-signature"></i>
                                                {% elif permissao.acesso == 'ADMINISTRAR' %}
                                                    <i class="fas fa-user-shield"></i>
                                                {% endif %}
                                                {{ permissao.acesso|title }}
                                            </span>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <!-- Resumo das Permissões -->
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <h6 class="card-title"><i class="fas fa-info-circle"></i> Resumo das Permissões</h6>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <ul class="list-unstyled">
                                                    <li><strong>Total de Módulos:</strong> {{ permissoes_por_modulo|length }}</li>
                                                    <li><strong>Total de Permissões:</strong> {{ permissoes_count }}</li>
                                                </ul>
                                            </div>
                                            <div class="col-md-6">
                                                <ul class="list-unstyled">
                                                    <li><strong>Módulos com Acesso:</strong> 
                                                        {% for modulo in permissoes_por_modulo.keys %}
                                                            <span class="badge bg-info">{{ modulo|title }}</span>
                                                        {% endfor %}
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% else %}
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle"></i>
                            <strong>Atenção:</strong> Este cargo/função não possui permissões definidas.
                            <br>
                            <small>Clique em "Editar Permissões" para configurar as permissões deste cargo/função.</small>
                        </div>
                    {% endif %}
                    
                    <div class="text-center mt-3">
                        <a href="{% url 'militares:cargo_funcao_update' cargo.id %}" class="btn btn-primary">
                            <i class="fas fa-edit"></i> Editar Permissões
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Seção de Usuários com esta Função -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="fas fa-users"></i> Usuários com esta Função</h5>
                </div>
                <div class="card-body">
                    {% if usuarios_com_funcao %}
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Nome</th>
                                        <th>Status</th>
                                        <th>Tipo</th>
                                        <th>Data Início</th>
                                        <th>Data Fim</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for usuario_funcao in usuarios_com_funcao %}
                                    <tr>
                                        <td>{{ usuario_funcao.usuario.get_full_name }}</td>
                                        <td>
                                            {% if usuario_funcao.status == 'ATIVO' %}
                                                <span class="badge bg-success">Ativo</span>
                                            {% elif usuario_funcao.status == 'INATIVO' %}
                                                <span class="badge bg-danger">Inativo</span>
                                            {% elif usuario_funcao.status == 'SUSPENSO' %}
                                                <span class="badge bg-warning">Suspenso</span>
                                            {% endif %}
                                        </td>
                                        <td>{{ usuario_funcao.get_tipo_funcao_display }}</td>
                                        <td>{{ usuario_funcao.data_inicio|date:"d/m/Y" }}</td>
                                        <td>{{ usuario_funcao.data_fim|date:"d/m/Y"|default:"-" }}</td>
                                        <td>
                                            <a href="{% url 'militares:usuario_funcao_update' usuario_funcao.id %}" class="btn btn-sm btn-primary">
                                                <i class="fas fa-edit"></i>
                                            </a>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    {% else %}
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i>
                            <strong>Informação:</strong> Nenhum usuário possui esta função atualmente.
                        </div>
                    {% endif %}
                    
                    <div class="text-center mt-3">
                        <a href="{% url 'militares:adicionar_usuario_cargo' cargo.id %}" class="btn btn-success">
                            <i class="fas fa-plus"></i> Adicionar Usuário
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    # Salvar o template recriado
    with open('militares/templates/militares/cargos/cargo_funcao_detail.html', 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("✅ Template de detalhes recriado com sucesso!")
    print("🎮 Agora acesse /militares/cargos/1/ para ver todos os módulos!")

if __name__ == "__main__":
    recriar_template_detalhes() 