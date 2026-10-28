export class AuthValidator {
    validate({ name, email, password }, mode) {
        const errors = {};

        // Validação do nome
        if (mode === "register" && name.length < 2) {
            errors.name =
                "Informe seu nome (pelo menos 2 caracteres).";
        }

        // Validação do e-mail
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            errors.email = "Digite um e-mail válido.";
        }

        // Validação da senha
        if (!password) {
            errors.password = "Digite sua senha.";
        } else if (mode === "register" && password.length < 10) {
            errors.password =
                "A senha precisa ter pelo menos 10 caracteres.";
        }

        return errors;
    }
}