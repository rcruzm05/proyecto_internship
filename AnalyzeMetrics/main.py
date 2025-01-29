import time
from google.cloud import monitoring_v3
import json
from google.cloud import pubsub_v1

def get_instance_metrics(request):
    # Extraer parámetros de la solicitud HTTP
    request_json = request.get_json(silent=True)
    project_id = request_json.get("project_id", "")
    instance_id = request_json.get("instance_id", "")
    zone = request_json.get("zone", "us-central1-c")
    duration = request_json.get("duration", 600)
    # Desclaración del tema
    topic_name = f"projects/{project_id}/topics/alerts-topic"

    # Inicializar cliente de Monitoring
    client = monitoring_v3.MetricServiceClient()

    # Inicializar cliente de Pub/Sub
    publisher = pubsub_v1.PublisherClient()

    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)

    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - duration), "nanos": nanos},
        }
    )

    metrics = {
        "cpu": "compute.googleapis.com/instance/cpu/utilization",
        "memory": "agent.googleapis.com/memory/percent_used",
        "swap": "agent.googleapis.com/swap/percent_used",
        "disk": "agent.googleapis.com/disk/percent_used",
    }

    thresholds = {
        "cpu": 0.95,
        "memory": 100.0,
        "swap": 85.0,
        "disk": 90.0,
    }

    alerts = []

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
                "name": f"projects/{project_id}",
                "filter": filters,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )

        for result in results:
            for point in result.points:
                start_time = point.interval.start_time.timestamp()
                value = point.value.double_value
                metric_labels = dict(result.metric.labels)

                alert_data = {
                    "metric": {
                        "type": metric_type,
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

                if value > thresholds[metric_name]:
                    if metric_name == "disk":
                        device = result.metric.labels.get("device", "unknown")
                        alert_data["device"] = device
                    alerts.append(alert_data)
    # Publicar alertas en Pub/Sub
    for alert in alerts:
        message = json.dumps(alert).encode("utf-8")  # Serializar como JSON
        future = publisher.publish(topic_name, message)

    return {"alerts": alerts, "count": len(alerts)}
