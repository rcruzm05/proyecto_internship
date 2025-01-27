import functions_framework
import requests
import logging
import json

# Configurar el nivel de los logs
logging.basicConfig(level=logging.INFO)

@functions_framework.http
def avatar_app(request):
    logging.info("Solicitud recibida")

    # Obtener el cuerpo de la solicitud como JSON
    try:
        request_json = request.get_json(silent=True)
        logging.info("Contenido completo de la solicitud: %s", json.dumps(request_json, indent=2))
    except Exception as e:
        logging.error("Error al procesar el cuerpo de la solicitud: %s", e)
        return {"text": "Error al procesar la solicitud. Inténtalo de nuevo."}

    # Validar la estructura de la solicitud
    if not request_json or "message" not in request_json:
        logging.warning("El evento no contiene 'message': %s", request_json)
        return {"text": "Solicitud inválida. No se encontró un comando válido."}

    # Extraer el mensaje de la solicitud
    message = request_json["message"]

    # Obtener el texto del comando desde argumentText
    command_text = message.get("argumentText", "").strip()
    logging.info("Texto del comando recibido: %s", command_text)

    # Verificar y procesar el comando
    command_parts = command_text.split()
    if len(command_parts) != 4:
        logging.warning("Comando inválido: %s", command_text)
        #return {"text": "Comando inválido. Usa: /postmortem PROJECT_ID INSTANCE_ID ZONE DURATION"}
        response_data = {"text": "Comando inválido. Usa: /postmortem PROJECT_ID INSTANCE_ID ZONE DURATION"}
        logging.warning("Respuesta enviada al chat: %s", response_data)
        return response_data

    # Extraer los argumentos del comando
    project_id, instance_id, zone, duration = command_parts
    logging.info("Parámetros extraídos: project_id=%s, instance_id=%s, zone=%s, duration=%s",
                 project_id, instance_id, zone, duration)

    # Construir el payload para la función externa
    metrics_payload = {
        "project_id": project_id,
        "instance_id": instance_id,
        "zone": zone,
        "duration": int(duration)
    }
    logging.info("Payload construido: %s", metrics_payload)

    # URL de la función externa
    metrics_function_url = "https://us-central1-sit-devops-testing.cloudfunctions.net/get_instance_metrics"

    try:
        # Llamar a la función externa
        logging.info("Realizando POST a %s", metrics_function_url)
        response = requests.post(metrics_function_url, json=metrics_payload)
        response_data = response.json()

        logging.info("Respuesta de la función externa: %s", response_data)

        if response.status_code == 200:
            alerts = response_data.get("alerts", [])
            alert_count = response_data.get("count", 0)

            if alert_count > 0:
                alert_details = "\n".join(
                    [f"- Métrica: {alert['metric']['type']}, Valor: {alert['points'][0]['value']['double_value']}"
                     for alert in alerts]
                )
                logging.warning("Respuesta devuelta: %s", f"Se detectaron {alert_count} alertas:\n{alert_details}")
                return {"text": f"Se detectaron {alert_count} alertas:\n{alert_details}"}
            else:
                logging.warning("Respuesta devuelta: %s", "No se detectaron alertas en la instancia especificada.")
                return {"text": "No se detectaron alertas en la instancia especificada."}
        else:
            logging.error("Error en la respuesta de la función externa: %s", response.text)
            return {"text": f"Error al obtener métricas: {response.text}"}
    except Exception as e:
        logging.exception("Ocurrió un error al llamar a la función externa")
        return {"text": f"Ocurrió un error: {str(e)}"}
