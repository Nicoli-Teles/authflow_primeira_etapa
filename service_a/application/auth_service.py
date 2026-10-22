import logging, re, uuid
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure.user_repository import SQLiteUserRepository
from infrastructure.event_publisher import WelcomeEventPublisher
log = logging.getLogger(__name__)

class AuthService:
    def __init__(self, repository=None, publisher=None):
        self.repository = repository or SQLiteUserRepository()
        self.publisher = publisher or WelcomeEventPublisher()
    def register(self, name, email, password):
        name, email = (name or "").strip(), (email or "").strip().lower()
        if len(name) < 2 or len(name) > 100: raise ValueError("Informe um nome com pelo menos 2 caracteres.")
        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): raise ValueError("Informe um e-mail válido.")
        if len(password or "") < 10: raise ValueError("A senha precisa ter pelo menos 10 caracteres.")
        if len(password) > 128: raise ValueError("A senha excede o tamanho permitido.")
        if self.repository.find_by_email(email): raise ValueError("Já existe uma conta com esse e-mail.")
        user = self.repository.create(name, email, generate_password_hash(password))
        event = {"event_id": str(uuid.uuid4()), "event_type": "user_registered", "user_id": user.id, "name": user.name, "email": user.email}
        try:
            self.publisher.publish_user_registered(event)
            queued = True
        except Exception:
            queued = False
            log.exception("event_publish_failed event_id=%s user_id=%s", event["event_id"], user.id)
        log.info("user_registered user_id=%s event_id=%s queued=%s", user.id, event["event_id"], queued)
        return {"id": user.id, "name": user.name, "email": user.email, "welcome_email_queued": queued,
                "message": "Conta criada! Evento enviado para a fila." if queued else "Conta criada, mas não foi possível publicar o e-mail de boas-vindas."}
    def login(self, email, password):
        user = self.repository.find_by_email((email or "").strip().lower())
        if not user or not check_password_hash(user.password_hash, password or ""):
            raise PermissionError("E-mail ou senha incorretos.")
        log.info("login_success user_id=%s", user.id)
        return {"id": user.id, "name": user.name, "email": user.email, "message": f"Olá, {user.name}! Login realizado com sucesso."}
