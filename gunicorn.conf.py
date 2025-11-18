# Configuração Gunicorn para SEPROM CBMEPI
# Salve em: /home/seprom/sepromcbmepi/gunicorn.conf.py

import multiprocessing
import os

# Configurações básicas
bind = "127.0.0.1:8000"  # TCP para compatibilidade com Nginx
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configurações de timeout
timeout = 60
keepalive = 2
graceful_timeout = 30

# Configurações de logging
accesslog = "/home/seprom/sepromcbmepi/logs/gunicorn_access.log"
errorlog = "/home/seprom/sepromcbmepi/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de processo
preload_app = True
daemon = False
pidfile = "/home/seprom/sepromcbmepi/gunicorn.pid"
user = "seprom"
group = "www-data"
tmp_upload_dir = None

# Configurações de worker
worker_tmp_dir = "/dev/shm"
worker_exit_on_app_exit = True

# Configurações de reload
reload = False
reload_extra_files = []

# Configurações de stats
statsd_host = None
statsd_prefix = "gunicorn"

# Configurações de SSL (se necessário)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

def when_ready(server):
    """Callback executado quando o servidor estiver pronto"""
    server.log.info("Gunicorn está pronto para receber conexões")

def on_starting(server):
    """Callback executado quando o servidor estiver iniciando"""
    server.log.info("Gunicorn está iniciando...")

def on_reload(server):
    """Callback executado quando o servidor for recarregado"""
    server.log.info("Gunicorn foi recarregado")

def worker_int(worker):
    """Callback executado quando um worker for interrompido"""
    worker.log.info("Worker %s foi interrompido", worker.pid)

def pre_fork(server, worker):
    """Callback executado antes de criar um worker"""
    server.log.info("Criando worker %s", worker.pid)

def post_fork(server, worker):
    """Callback executado após criar um worker"""
    server.log.info("Worker %s foi criado", worker.pid)

def post_worker_init(worker):
    """Callback executado após inicializar um worker"""
    worker.log.info("Worker %s foi inicializado", worker.pid)

def worker_abort(worker):
    """Callback executado quando um worker for abortado"""
    worker.log.info("Worker %s foi abortado", worker.pid)
