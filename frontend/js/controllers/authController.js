export class AuthController {
    constructor(authService, authValidator, authView) {
        this.authService = authService;
        this.authValidator = authValidator;
        this.authView = authView;

        this.mode = "login";
    }

    init() {
        const view = this.authView;

        view.setMode(this.mode);

        view.loginTab.addEventListener("click", () => {
            this.setMode("login");
        });

        view.registerTab.addEventListener("click", () => {
            this.setMode("register");
        });

        // Usa delegação de eventos para o botão dinâmico
        view.switchCopy.addEventListener("click", event => {
            if (!event.target.closest("#switch-action")) {
                return;
            }

            this.setMode(
                this.mode === "register" ? "login" : "register"
            );
        });

        view.togglePassword.addEventListener("click", () => {
            view.togglePasswordVisibility();
        });

        view.form.addEventListener("submit", event => {
            this.handleSubmit(event);
        });

        view.refreshIcons();
    }

    setMode(mode) {
        this.mode = mode;
        this.authView.setMode(mode);
    }

    async handleSubmit(event) {
        event.preventDefault();

        const view = this.authView;
        const data = view.getFormData();

        view.clearErrors();
        view.hideNotice();

        // Valida os dados antes de chamar a API
        const errors = this.authValidator.validate(data, this.mode);

        if (Object.keys(errors).length > 0) {
            view.renderErrors(errors);
            return;
        }

        const originalMode = this.mode;

        view.setLoading(true, originalMode);

        try {
            let response;

            if (originalMode === "register") {
                response = await this.authService.register(data);
            } else {
                response = await this.authService.login(data);
            }

            if (originalMode === "register") {
                this.setMode("login");
                view.setEmail(data.email);

                view.showNotice(
                    response.message ||
                        "Conta criada. Agora você pode entrar.",
                    response.welcome_email_queued === false
                        ? "error"
                        : "success"
                );
            } else {
                view.showNotice(
                    response.message || "Login realizado com sucesso.",
                    "success"
                );
            }

        } catch (error) {
            view.showNotice(
                error.message ||
                    "Não foi possível conectar ao servidor.",
                "error"
            );

        } finally {
            view.setLoading(false, this.mode);
        }
    }
}