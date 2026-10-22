from flask import Flask, jsonify, request
from application.auth_service import AuthService

def create_app():
    app = Flask(__name__)
    service = AuthService()
    @app.get("/api/health")
    def health():
        return jsonify({"status":"ok","service":"service-a"})
    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        try:
            result = service.register(data.get("name",""), data.get("email",""), data.get("password",""))
            return jsonify(result), 201 if result["welcome_email_queued"] else 202
        except ValueError as exc:
            return jsonify({"error":str(exc)}), 400
        except Exception:
            app.logger.exception("register_failed")
            return jsonify({"error":"Não foi possível criar a conta neste momento."}), 500
    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        try: return jsonify(service.login(data.get("email",""), data.get("password",""))), 200
        except PermissionError as exc: return jsonify({"error":str(exc)}), 401
        except Exception:
            app.logger.exception("login_failed")
            return jsonify({"error":"Não foi possível realizar o login neste momento."}), 500
    return app
