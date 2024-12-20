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

    # Consultar métricas
    for metric_name, metric_type in metrics.items():
        # Condición adicional para métricas con atributo "state = used"
        if metric_name in ["memory", "swap", "disk"]:
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

        # Procesamiento de la métrica disco (separar por sistema de archivos)
        if metric_name == "disk":
            device_logs = {}
            for result in results:
                device = result.metric.labels.get("device", "unknown")
                if device not in device_logs:
                    device_logs[device] = []
                for point in result.points:
                    #start_time = point.interval.start_time
                    # Se usa timestamp() para conservar la hora en epoch
                    start_time = point.interval.start_time.timestamp()
                    value = point.value.double_value
                    device_logs[device].append({"time": start_time, "value": value})

            # Imprimir resultados separados por dispositivo
            for device, logs in device_logs.items():
                print(f"  Dispositivo {device}:")
                for log in logs:
                    print(f"    Time: {log['time']} - Value: {log['value']}")
        else:
            # Para las otras métricas
            for result in results:
                for point in result.points:
                    #start_time = point.interval.start_time
                    # Se usa timestamp() para conservar la hora en epoch
                    start_time = point.interval.start_time.timestamp()
                    value = point.value.double_value
                    print(f"  Time: {start_time} - Value: {value}")

        print("\n")

# Uso del script
project_id = 'sit-devops-training'
instance_id = '4609971122707751401'
zone = 'us-central1-c'
duration = 600 

get_instance_metrics(project_id, instance_id, zone, duration)