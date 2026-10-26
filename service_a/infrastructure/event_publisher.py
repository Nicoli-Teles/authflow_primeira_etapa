
import json
import os
import logging
import pika

log = logging.getLogger(__name__)


class WelcomeEventPublisher:
    def publish_event(self, event):
        credentials = pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "appuser"),
            os.getenv(
                "RABBITMQ_PASSWORD",
                "change_this_local_password"
            )
        )

        params = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            credentials=credentials,
            heartbeat=30,
            connection_attempts=5,
            retry_delay=2
        )

        conn = pika.BlockingConnection(params)

        try:
            ch = conn.channel()
            queue = os.getenv("RABBITMQ_QUEUE", "welcome_emails")

            ch.queue_declare(queue=queue, durable=True)

            # Habilita confirmação de publicação pelo RabbitMQ.
            ch.confirm_delivery()

            message = json.dumps(event).encode("utf-8")

            ch.basic_publish(
                exchange="",
                routing_key=queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                    message_id=event["event_id"],
                    type="user_registered"
                ),
                mandatory=True
            )

            # Com confirmações habilitadas, o Pika pode lançar
            # uma exceção se a publicação não for confirmada.
            # Se basic_publish retornar normalmente, consideramos
            # a publicação confirmada.
            log.info(
                "event_published event_id=%s",
                event["event_id"]
            )

        except Exception:
            log.exception(
                "rabbitmq_publish_error event_id=%s",
                event.get("event_id")
            )
            raise

        finally:
            if conn.is_open:
                conn.close()
