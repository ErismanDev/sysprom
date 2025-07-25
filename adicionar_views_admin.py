#!/usr/bin/env python
"""
Script para adicionar views de admin ao arquivo views.py
"""
import os

def adicionar_views_admin():
    """Adiciona as views de admin ao final do arquivo views.py"""
    
    print("🔧 ADICIONANDO VIEWS DE ADMIN")
    print("=" * 50)
    
    # Ler o arquivo views.py
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ler o arquivo com as views de admin
    with open('views_admin.py', 'r', encoding='utf-8') as f:
        views_admin = f.read()
    
    # Remover comentários e linhas vazias do início
    lines = views_admin.split('\n')
    start_index = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            start_index = i
            break
    
    views_admin_content = '\n'.join(lines[start_index:])
    
    # Adicionar ao final do arquivo
    content += '\n\n' + views_admin_content
    
    # Salvar arquivo
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Views de admin adicionadas ao arquivo views.py!")

def adicionar_urls_admin():
    """Adiciona as URLs de admin ao arquivo urls.py"""
    
    print("\n🔗 ADICIONANDO URLS DE ADMIN")
    print("=" * 50)
    
    # Ler o arquivo urls.py
    with open('militares/urls.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # URLs para adicionar
    urls_admin = '''
    # URLs para gerenciamento de usuários admin
    path('usuarios/admin/', views.gerenciar_usuarios_admin, name='gerenciar_usuarios_admin'),
    path('usuarios/admin/criar/', views.criar_usuario_admin_web, name='criar_usuario_admin'),
    path('usuarios/admin/listar/', views.listar_usuarios_admin_web, name='listar_usuarios_admin'),
    path('usuarios/admin/remover/<int:user_id>/', views.remover_usuario_admin_web, name='remover_usuario_admin'),
'''
    
    # Encontrar onde adicionar (antes do último fechamento de parênteses)
    last_paren = content.rfind(')')
    if last_paren != -1:
        content = content[:last_paren] + urls_admin + content[last_paren:]
        
        # Salvar arquivo
        with open('militares/urls.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ URLs de admin adicionadas ao arquivo urls.py!")
    else:
        print("❌ Não foi possível encontrar onde adicionar as URLs")

def criar_templates_admin():
    """Cria os templates para gerenciamento de admin"""
    
    print("\n📄 CRIANDO TEMPLATES DE ADMIN")
    print("=" * 50)
    
    # Criar diretório se não existir
    os.makedirs('militares/templates/militares/usuarios', exist_ok=True)
    
    # Template principal
    template_principal = '''{% extends 'base.html' %}

{% block title %}Gerenciar Usuários Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-users-cog"></i>
                        Gerenciar Usuários Administradores
                    </h3>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="info-box">
                                <span class="info-box-icon bg-primary">
                                    <i class="fas fa-users"></i>
                                </span>
                                <div class="info-box-content">
                                    <span class="info-box-text">Total de Admins</span>
                                    <span class="info-box-number">{{ total_admins }}</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="info-box">
                                <span class="info-box-icon bg-success">
                                    <i class="fas fa-user-check"></i>
                                </span>
                                <div class="info-box-content">
                                    <span class="info-box-text">Admins Ativos</span>
                                    <span class="info-box-number">{{ admins_ativos }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-12">
                            <a href="{% url 'militares:criar_usuario_admin' %}" class="btn btn-primary">
                                <i class="fas fa-plus"></i>
                                Criar Novo Admin
                            </a>
                            <a href="{% url 'militares:listar_usuarios_admin' %}" class="btn btn-info">
                                <i class="fas fa-list"></i>
                                Listar Admins
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    # Template para criar admin
    template_criar = '''{% extends 'base.html' %}

{% block title %}Criar Usuário Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-user-plus"></i>
                        Criar Novo Usuário Administrador
                    </h3>
                </div>
                <div class="card-body">
                    <form method="post">
                        {% csrf_token %}
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="username">Username *</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="email">Email</label>
                                    <input type="email" class="form-control" id="email" name="email">
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="first_name">Nome</label>
                                    <input type="text" class="form-control" id="first_name" name="first_name">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="last_name">Sobrenome</label>
                                    <input type="text" class="form-control" id="last_name" name="last_name">
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="password">Senha *</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-group">
                                    <label for="confirm_password">Confirmar Senha *</label>
                                    <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-12">
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save"></i>
                                    Criar Admin
                                </button>
                                <a href="{% url 'militares:gerenciar_usuarios_admin' %}" class="btn btn-secondary">
                                    <i class="fas fa-arrow-left"></i>
                                    Voltar
                                </a>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    # Template para listar admins
    template_listar = '''{% extends 'base.html' %}

{% block title %}Listar Usuários Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-users"></i>
                        Usuários Administradores
                    </h3>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Username</th>
                                    <th>Nome</th>
                                    <th>Email</th>
                                    <th>Função</th>
                                    <th>Status</th>
                                    <th>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for admin in admins %}
                                <tr>
                                    <td>
                                        <strong>{{ admin.username }}</strong>
                                        {% if admin.is_superuser %}
                                            <span class="badge badge-primary">Super</span>
                                        {% endif %}
                                    </td>
                                    <td>{{ admin.get_full_name|default:"N/A" }}</td>
                                    <td>{{ admin.email|default:"N/A" }}</td>
                                    <td>
                                        {% if admin.funcao_ativa %}
                                            {{ admin.funcao_ativa.cargo_funcao.nome }}
                                        {% else %}
                                            <span class="text-muted">Nenhuma função</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if admin.is_active %}
                                            <span class="badge badge-success">Ativo</span>
                                        {% else %}
                                            <span class="badge badge-danger">Inativo</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if admin.username != 'admin' %}
                                            <a href="{% url 'militares:remover_usuario_admin' admin.id %}" 
                                               class="btn btn-danger btn-sm"
                                               onclick="return confirm('Tem certeza que deseja remover este usuário admin?')">
                                                <i class="fas fa-trash"></i>
                                                Remover
                                            </a>
                                        {% else %}
                                            <span class="text-muted">Admin Principal</span>
                                        {% endif %}
                                    </td>
                                </tr>
                                {% empty %}
                                <tr>
                                    <td colspan="6" class="text-center">Nenhum usuário admin encontrado</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="mt-3">
                        <a href="{% url 'militares:gerenciar_usuarios_admin' %}" class="btn btn-secondary">
                            <i class="fas fa-arrow-left"></i>
                            Voltar
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    # Salvar templates
    with open('militares/templates/militares/usuarios/gerenciar_usuarios_admin.html', 'w', encoding='utf-8') as f:
        f.write(template_principal)
    
    with open('militares/templates/militares/usuarios/criar_usuario_admin.html', 'w', encoding='utf-8') as f:
        f.write(template_criar)
    
    with open('militares/templates/militares/usuarios/listar_usuarios_admin.html', 'w', encoding='utf-8') as f:
        f.write(template_listar)
    
    print("✅ Templates de admin criados!")

if __name__ == "__main__":
    adicionar_views_admin()
    adicionar_urls_admin()
    criar_templates_admin()
    print("\n🎉 Sistema de gerenciamento de usuários admin configurado!") 