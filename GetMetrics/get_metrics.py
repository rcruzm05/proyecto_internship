import time
from google.cloud import monitoring_v3

def get_instance_metrics(project_id, instance_id, zone, duration):
    # Inicializar cliente de Monitoring y Compute Engine
    client = monitoring_v3.MetricServiceClient()

    # Definir tiempo de consulta
    project_name = f"projects/{project_id}"
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)

    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - duration), "nanos": nanos},
        }
    )

    # Métricas a consultar
    metrics = {
        "cpu": "compute.googleapis.com/instance/cpu/utilization",
        "memory": "agent.googleapis.com/memory/percent_used",
        "disk": "agent.googleapis.com/disk/percent_used",
        "swap": "agent.googleapis.com/memory/swap/percent_used"
    }

    # Consultar mtricas
    for metric_name, metric_type in metrics.items():
        filters = (
            f'metric.type = "{metric_type}" AND '
            f'resource.labels.instance_id = "{instance_id}" AND '
            f'resource.labels.zone = "{zone}"'
        )

        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": filters,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        # Imprimir resultados
        print(f"Resultados para {metric_name}:")
        for result in results:
            print(result)
        print("\n")

# Configuración de parámetros de instancia
project_id = ""
instance_id= ""
zone = ""
duration = 1200

get_instance_metrics(project_id, instance_id, zone, duration)