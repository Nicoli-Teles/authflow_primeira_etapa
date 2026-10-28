export class AuthView {
    constructor() {
        this.form = document.querySelector("#auth-form");

        this.loginTab = document.querySelector("#login-tab");
        this.registerTab = document.querySelector("#register-tab");

        this.nameField = document.querySelector("#name-field");
        this.nameInput = document.querySelector("#name");
        this.emailInput = document.querySelector("#email");
        this.passwordInput = document.querySelector("#password");

        this.notice = document.querySelector("#notice");
        this.submitButton = document.querySelector("#submit-button");
        this.submitLabel = document.querySelector("#submit-label");

        this.formKicker = document.querySelector("#form-kicker");
        this.formTitle = document.querySelector("#form-title");
        this.formSubtitle = document.querySelector("#form-subtitle");
        this.passwordHint = document.querySelector("#password-hint");
        this.switchCopy = document.querySelector("#switch-copy");
        this.togglePassword = document.querySelector("#toggle-password");
    }

    setMode(mode) {
        const isRegister = mode === "register";

        this.nameField.classList.toggle("hidden", !isRegister);
        this.nameInput.required = isRegister;

        this.loginTab.classList.toggle("active", !isRegister);
        this.registerTab.classList.toggle("active", isRegister);

        this.loginTab.setAttribute("aria-selected", String(!isRegister));
        this.registerTab.setAttribute("aria-selected", String(isRegister));

        this.formKicker.textContent = isRegister
            ? "COMECE SUA JORNADA"
            : "BEM-VINDA(O) DE VOLTA";

        this.formTitle.textContent = isRegister
            ? "Crie sua conta."
            : "Que bom ter você aqui.";

        this.formSubtitle.textContent = isRegister
            ? "Só precisamos de alguns dados para começar."
            : "Entre com seus dados para continuar.";

        this.submitLabel.textContent = isRegister
            ? "Criar minha conta"
            : "Entrar na minha conta";

        this.passwordInput.autocomplete = isRegister
            ? "new-password"
            : "current-password";

        this.passwordHint.textContent = isRegister
            ? "Use pelo menos 10 caracteres."
            : "Use a senha cadastrada na sua conta.";

        // Atualiza o texto e o botão de alternância
        const button = document.createElement("button");

        button.type = "button";
        button.id = "switch-action";
        button.textContent = isRegister
            ? "Entrar"
            : "Criar conta grátis";

        const message = document.createTextNode(
            isRegister
                ? "Já tem uma conta? "
                : "Ainda não tem uma conta? "
        );

        this.switchCopy.replaceChildren(message, button);

        this.clearErrors();
        this.hideNotice();
        this.form.reset();

        this.refreshIcons();
    }

    getFormData() {
        return {
            name: this.nameInput.value.trim(),
            email: this.emailInput.value.trim(),
            password: this.passwordInput.value
        };
    }

    setEmail(email) {
        this.emailInput.value = email;
    }

    clearErrors() {
        document.querySelectorAll(".field-error").forEach(error => {
            error.textContent = "";
        });
    }

    renderErrors(errors) {
        const fields = {
            name: "#name-error",
            email: "#email-error",
            password: "#password-error"
        };

        Object.entries(errors).forEach(([field, message]) => {
            const element = document.querySelector(fields[field]);

            if (element) {
                element.textContent = message;
            }
        });
    }

    showNotice(message, type) {
        this.notice.textContent = message;
        this.notice.className = `notice ${type}`;
    }

    hideNotice() {
        this.notice.textContent = "";
        this.notice.className = "notice hidden";
    }

    setLoading(isLoading, mode) {
        this.submitButton.disabled = isLoading;

        if (isLoading) {
            this.submitLabel.textContent = mode === "register"
                ? "Criando sua conta..."
                : "Verificando acesso...";

            return;
        }

        this.submitLabel.textContent = mode === "register"
            ? "Criar minha conta"
            : "Entrar na minha conta";
    }

    togglePasswordVisibility() {
        const showPassword = this.passwordInput.type === "password";

        this.passwordInput.type = showPassword ? "text" : "password";

        this.togglePassword.innerHTML =
            `<i data-lucide="${showPassword ? "eye-off" : "eye"}"></i>`;

        this.refreshIcons();
    }

    refreshIcons() {
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }
}