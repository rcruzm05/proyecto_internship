import time
from google.cloud import monitoring_v3

def get_instance_metrics(project_id, instance_id, zone, duration):
    # Inicializar cliente de Monitoring
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
        "swap": "agent.googleapis.com/swap/percent_used",
        "disk": "agent.googleapis.com/disk/percent_used",
    }

    for metric_name, metric_type in metrics.items():
        # Condición adicional para métricas con atributo "state = used"
        if metric_name != "cpu":
            state_filter = 'AND metric.labels.state = "used"'
        else:
            state_filter = ""

        filters = (
            f'metric.type = "{metric_type}" AND '
            f'resource.labels.instance_id = "{instance_id}" AND '
            f'resource.labels.zone = "{zone}" {state_filter}'
        )

        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": filters,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        print(f"Resultados para {metric_name}:")

        for result in results:
            for point in result.points:
                # Se usa timestamp() para conservar la hora en epoch
                start_time = point.interval.start_time.timestamp()
                value = point.value.double_value
                if metric_name == "disk":
                    device = result.metric.labels.get("device", "unknown")
                    print(f"  Device: {device} - Time: {start_time} - Value: {value}")
                else:
                    print(f"  Time: {start_time} - Value: {value}")

project_id = 'sit-devops-training'
instance_id = '4609971122707751401'
zone = 'us-central1-c'
duration = 600 

get_instance_metrics(project_id, instance_id, zone, duration)