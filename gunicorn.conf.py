#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuração do Gunicorn para otimização de performance
"""

import os
import multiprocessing

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 2  # Reduzido para evitar sobrecarga de memória
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120  # Aumentado para 2 minutos
keepalive = 2
preload_app = True

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
worker_tmp_dir = "/dev/shm"  # Usar memória compartilhada
worker_abort_on_app_exit = True

# Configurações de graceful shutdown
graceful_timeout = 30
preload_app = True

# Configurações de debug
reload = False
reload_engine = "auto"

def when_ready(server):
    """Chamado quando o servidor está pronto"""
    server.log.info("🚀 Gunicorn iniciado com configurações otimizadas")

def worker_int(worker):
    """Chamado quando um worker é interrompido"""
    worker.log.info("⚠️ Worker interrompido")

def worker_abort(worker):
    """Chamado quando um worker é abortado"""
    worker.log.info("❌ Worker abortado")

def pre_fork(server, worker):
    """Chamado antes de criar um worker"""
    server.log.info(f"🔄 Criando worker {worker.pid}")

def post_fork(server, worker):
    """Chamado após criar um worker"""
    server.log.info(f"✅ Worker {worker.pid} criado")

def post_worker_init(worker):
    """Chamado após inicializar um worker"""
    worker.log.info(f"🎯 Worker {worker.pid} inicializado")

def worker_exit(server, worker):
    """Chamado quando um worker sai"""
    server.log.info(f"👋 Worker {worker.pid} saiu") 