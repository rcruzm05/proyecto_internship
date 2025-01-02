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

    # Diccionario para almacenar las métricas recopiladas
    metrics_data = {"cpu": [], "memory": [], "swap": [], "disk": {}}

    for metric_name, metric_type in metrics.items():
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
                start_time = point.interval.start_time.timestamp()
                value = point.value.double_value

                if metric_name == "disk":
                    device = result.metric.labels.get("device", "unknown")
                    if device not in metrics_data["disk"]:
                        metrics_data["disk"][device] = []
                    print(f"  Device: {device} - Time: {start_time} - Value: {value}")
                    metrics_data["disk"][device].append({"time": start_time, "value": value})
                else:
                    print(f"  Time: {start_time} - Value: {value}")
                    metrics_data[metric_name].append({"time": start_time, "value": value})

    # Verificar umbrales al final
    alerts = check_thresholds(metrics_data) 
    for alert in alerts:
        print(alert)

# Función para verificar umbrales
def check_thresholds(metrics_data):
    thresholds = {
        "cpu": 0.95,
        "memory": 100.0,
        "swap": 85.0,
        "disk": 90.0,
    }
    
    alerts = []

    for metric_name, data in metrics_data.items():
        if metric_name == "disk":
            for device, logs in data.items():
                for log in logs:
                    time = log["time"]
                    value = log["value"]
                    if value > thresholds[metric_name]:
                        alerts.append(f"CRITICAL: Disk on {device} at {time} has only {value}% free space")
        else:
            for log in data:
                time = log["time"]
                value = log["value"]
                if value > thresholds[metric_name]:
                    alerts.append(f"CRITICAL: {metric_name.upper()} at {time} has exceeded the threshold with value {value}")
    
    return alerts

project_id = 'sit-devops-training'
#instance_id = '4609971122707751401'
instance_id = '5359897555328800587'
zone = 'us-central1-c'
duration = 1200 

get_instance_metrics(project_id, instance_id, zone, duration)
