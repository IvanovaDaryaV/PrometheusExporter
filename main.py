from flask import Flask
from prometheus_client import Gauge, generate_latest
import psutil
import os

app = Flask(__name__)

# Метрики
cpu_usage_gauge = Gauge('cpu_usage', 'CPU usage per core', ['core'])
memory_total_gauge = Gauge('memory_total', 'Total system memory')
memory_used_gauge = Gauge('memory_used', 'Used system memory')
disk_total_gauge = Gauge('disk_total', 'Total disk space', ['device'])
disk_used_gauge = Gauge('disk_used', 'Used disk space', ['device'])

# Обновление метрик
def update_metrics():
    # CPU usage
    for i, usage in enumerate(psutil.cpu_percent(percpu=True)):
        cpu_usage_gauge.labels(core=f'core_{i}').set(usage)

    # Memory usage
    virtual_memory = psutil.virtual_memory()
    memory_total_gauge.set(virtual_memory.total)
    memory_used_gauge.set(virtual_memory.used)

    # Disk usage
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        disk_total_gauge.labels(device=part.device).set(usage.total)
        disk_used_gauge.labels(device=part.device).set(usage.used)

@app.route('/')
def metrics():
    update_metrics()
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    host = os.getenv('EXPORTER_HOST', '0.0.0.0')
    port = int(os.getenv('EXPORTER_PORT', 8000))
    app.run(host=host, port=port)
