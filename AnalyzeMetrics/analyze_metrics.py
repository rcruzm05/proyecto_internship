import time
from google.cloud import monitoring_v3
import json  # Para manipular y guardar datos en formato JSON

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

    # Definir umbrales
    thresholds = {
        "cpu": 0.95,
        "memory": 100.0,
        "swap": 85.0,
        "disk": 90.0,
    }

    # Lista para almacenar los resultados que superen los umbrales
    alerts = []

    for metric_name, metric_type in metrics.items():
        ########
        print(metric_name)
        ########
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

        for result in results:
            for point in result.points:
                # Extraer la hora y el valor de la métrica
                start_time = point.interval.start_time.timestamp()
                value = point.value.double_value

                metric_labels = dict(result.metric.labels)

                # Crear el formato JSON para los datos
                alert_data = {
                    "metric": {
                        "type": metric_type,
                        #"labels": result.metric.labels,
                        "labels": metric_labels,
                    },
                    "points": [
                        {
                            "interval": {
                                "start_time": {"seconds": int(start_time)},
                                "end_time": {"seconds": int(start_time)},
                            },
                            "value": {"double_value": value},
                        }
                    ],
                }

                ### Codigo de prueba ###
                device = result.metric.labels.get("device", "unknown")
                if metric_name == "disk":
                    print(f"  Device: {device} - Time: {start_time} - Value: {value}")
                else:
                    print(f"  Time: {start_time} - Value: {value}")
                #########################

                # Verificar si supera el umbral
                if value > thresholds[metric_name]:
                    # Agregar información adicional para discos
                    if metric_name == "disk":
                        device = result.metric.labels.get("device", "unknown")
                        alert_data["device"] = device

                    # Añadir a la lista de alertas
                    alerts.append(alert_data)

    print(alerts)
    # Guardar las alertas en un archivo JSON
    with open("alerts.json", "w") as f:
        json.dump(alerts, f, indent=4)

    print(f"Se generaron {len(alerts)} alertas. Guardadas en 'alerts.json'.")


# Configuración del proyecto y detalles de la instancia
project_id = 'sit-devops-training'
instance_id = '4609971122707751401'
zone = 'us-central1-c'
duration = 600

get_instance_metrics(project_id, instance_id, zone, duration)
