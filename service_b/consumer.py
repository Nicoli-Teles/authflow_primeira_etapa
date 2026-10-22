import json, logging, os, smtplib, time
from email.message import EmailMessage
import pika
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("service-b")

def send_email(event):
    event_id, name, recipient = event.get("event_id","unknown"), event.get("name","Olá"), event["email"]
    if os.getenv("SMTP_ENABLED","false").lower() != "true":
        log.info("email_simulated event_id=%s recipient=%s name=%s", event_id, recipient, name)
        return
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = "Boas-vindas!", os.environ["SMTP_FROM"], recipient
    msg.set_content(f"Olá, {name}!\n\nSeja muito bem-vindo(a). Sua conta foi criada com sucesso.\n\nEstamos felizes por ter você conosco!")
    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT","587")), timeout=20) as smtp:
        smtp.ehlo()
        if os.getenv("SMTP_USE_TLS","true").lower() == "true":
            smtp.starttls(); smtp.ehlo()
        if os.getenv("SMTP_USERNAME"): smtp.login(os.environ["SMTP_USERNAME"], os.getenv("SMTP_PASSWORD",""))
        smtp.send_message(msg)
    log.info("welcome_email_sent event_id=%s recipient=%s", event_id, recipient)

def main():
    host = os.getenv("RABBITMQ_HOST","rabbitmq")
    credentials = pika.PlainCredentials(os.getenv("RABBITMQ_USER","appuser"), os.getenv("RABBITMQ_PASSWORD","change_this_local_password"))
    queue = os.getenv("RABBITMQ_QUEUE","welcome_emails")
    while True:
        conn = None
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials, heartbeat=30, connection_attempts=5, retry_delay=3))
            ch = conn.channel(); ch.queue_declare(queue=queue, durable=True); ch.basic_qos(prefetch_count=1)
            def callback(channel, method, props, body):
                event_id = "unknown"
                try:
                    event = json.loads(body.decode()); event_id = event.get("event_id","unknown")
                    if event.get("event_type") != "user_registered":
                        log.warning("unknown_event event_id=%s", event_id); channel.basic_ack(method.delivery_tag); return
                    log.info("event_received event_id=%s", event_id)
                    send_email(event)
                    channel.basic_ack(method.delivery_tag)
                    log.info("event_processed event_id=%s", event_id)
                except Exception:
                    log.exception("event_processing_failed event_id=%s; requeue=true", event_id)
                    channel.basic_nack(method.delivery_tag, requeue=True); time.sleep(3)
            ch.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)
            log.info("consumer_ready queue=%s", queue); ch.start_consuming()
        except KeyboardInterrupt: break
        except Exception:
            log.exception("rabbitmq_connection_failed; retrying")
            time.sleep(5)
        finally:
            if conn and conn.is_open: conn.close()
if __name__ == "__main__": main()
