"""
Gunicorn production config for alasadi_catalog.

Run with:
    gunicorn -c gunicorn_config.py alasadi_catalog.wsgi:application
"""

import multiprocessing

bind = "127.0.0.1:8000"

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2

timeout = 60
graceful_timeout = 30
keepalive = 5

max_requests = 1000
max_requests_jitter = 100

accesslog = "-"
errorlog = "-"
loglevel = "info"

proc_name = "alasadi_catalog"
