export class AuthService {
    async request(endpoint, payload) {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                data.error || "Não foi possível concluir a operação."
            );
        }

        return data;
    }

    register({ name, email, password }) {
        return this.request("/api/auth/register", {
            name,
            email,
            password
        });
    }

    login({ email, password }) {
        return this.request("/api/auth/login", {
            email,
            password
        });
    }
}