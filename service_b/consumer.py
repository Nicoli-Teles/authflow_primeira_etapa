import json, logging, os, smtplib, time
from email.message import EmailMessage
import pika
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("service-b")


def send_email(event):
    event_id = event.get("event_id", "unknown")
    name = event.get("name", "Olá")
    recipient = event["email"]
    event_type = event.get("event_type")

    if os.getenv("SMTP_ENABLED", "false").lower() != "true":
        log.info(
            "email_simulated event_id=%s recipient=%s type=%s",
            event_id, recipient, event_type
        )
        return

    if event_type == "user_registered":
        subject = "Boas-vindas!"
        body = (
            f"Olá, {name}!\n\n"
            "Seja muito bem-vindo(a). "
            "Sua conta foi criada com sucesso.\n\n"
            "Estamos felizes por ter você conosco!"
        )

    elif event_type == "user_logged_in":
        subject = "Que bom ter você conosco novamente!"
        body = (
            f"Olá, {name}!\n\n"
            "Que bom ter você conosco novamente!\n\n"
            "Detectamos um novo login na sua conta. "
            "Se foi você, não precisa fazer nada.\n\n"
            "Se você não reconhece esse acesso, "
            "recomendamos alterar sua senha imediatamente "
            "e entrar em contato com o suporte.\n\n"
            "Por segurança, nunca compartilhe sua senha "
            "por e-mail."
        )

    else:
        raise ValueError(f"Tipo de evento desconhecido: {event_type}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = recipient
    msg.set_content(body)

    with smtplib.SMTP(
        os.environ["SMTP_HOST"],
        int(os.getenv("SMTP_PORT", "587")),
        timeout=20
    ) as smtp:
        smtp.ehlo()

        if os.getenv("SMTP_USE_TLS", "true").lower() == "true":
            smtp.starttls()
            smtp.ehlo()

        if os.getenv("SMTP_USERNAME"):
            smtp.login(
                os.environ["SMTP_USERNAME"],
                os.getenv("SMTP_PASSWORD", "")
            )

        smtp.send_message(msg)

    log.info(
        "welcome_email_sent event_id=%s recipient=%s type=%s",
        event_id, recipient, event_type
    )


def main():
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "appuser"),
        os.getenv(
            "RABBITMQ_PASSWORD",
            "change_this_local_password"
        )
    )

    queue = os.getenv("RABBITMQ_QUEUE", "welcome_emails")

    while True:
        conn = None

        try:
            conn = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    credentials=credentials,
                    heartbeat=30,
                    connection_attempts=5,
                    retry_delay=3
                )
            )

            ch = conn.channel()
            ch.queue_declare(queue=queue, durable=True)
            ch.basic_qos(prefetch_count=1)

            def callback(channel, method, props, body):
                event_id = "unknown"

                try:
                    event = json.loads(body.decode("utf-8"))
                    event_id = event.get("event_id", "unknown")
                    event_type = event.get("event_type")

                    if event_type not in (
                        "user_registered",
                        "user_logged_in"
                    ):
                        log.warning(
                            "unknown_event event_id=%s type=%s",
                            event_id,
                            event_type
                        )
                        channel.basic_ack(method.delivery_tag)
                        return

                    log.info(
                        "event_received event_id=%s type=%s",
                        event_id,
                        event_type
                    )

                    send_email(event)

                    channel.basic_ack(method.delivery_tag)

                    log.info(
                        "event_processed event_id=%s type=%s",
                        event_id,
                        event_type
                    )

                except Exception:
                    log.exception(
                        "event_processing_failed event_id=%s; requeue=true",
                        event_id
                    )

                    channel.basic_nack(
                        method.delivery_tag,
                        requeue=True
                    )
                    time.sleep(3)

            ch.basic_consume(
                queue=queue,
                on_message_callback=callback,
                auto_ack=False
            )

            log.info("consumer_ready queue=%s", queue)
            ch.start_consuming()

        except KeyboardInterrupt:
            log.info("consumer_stopped")
            break

        except Exception:
            log.exception("rabbitmq_connection_failed; retrying")
            time.sleep(5)

        finally:
            if conn and conn.is_open:
                conn.close()


if __name__ == "__main__":
    main()

if __name__ == "__main__": main()
