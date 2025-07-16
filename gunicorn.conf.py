# Configuração Gunicorn para Digital Ocean
bind = "0.0.0.0:8080"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 120
keepalive = 5

# Logs
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190