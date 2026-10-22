# AuthFlow — primeira etapa

Aplicação didática com quatro containers: NGINX, Serviço A (autenticação), Serviço B (consumidor de e-mail) e RabbitMQ. O Serviço A não chama o Serviço B: publica `user_registered` no RabbitMQ.

## Rodar localmente
1. Instale e inicie o Docker Desktop.
2. No terminal, dentro desta pasta:
   - Windows PowerShell: `Copy-Item .env.example .env`
   - Linux/macOS: `cp .env.example .env`
3. Execute `docker compose up --build`.
4. Abra http://localhost:8080.
5. Cadastre uma conta e acompanhe `docker compose logs -f service-a service-b rabbitmq nginx`.

Por padrão `SMTP_ENABLED=false`: o Serviço B registra um envio simulado nos logs. Para enviar de verdade, preencha as variáveis SMTP no `.env` e mude `SMTP_ENABLED=true`. Use senha de app/credenciais SMTP do provedor e nunca faça commit do `.env`.

## Testar fila com consumidor parado
`docker compose stop service-b`, cadastre outra conta e depois `docker compose start service-b`. A fila durável deve guardar mensagens já publicadas enquanto o consumidor está parado. Não pare o RabbitMQ durante este teste.

## Encerrar
`docker compose down`. Para apagar também os volumes persistentes: `docker compose down -v` (apaga os dados locais).

## Camadas
- `service_a/domain`: entidade User.
- `service_a/application`: regras de cadastro e login.
- `service_a/infrastructure`: SQLite e publicação RabbitMQ.
- `service_a/presentation`: endpoints Flask.
- `service_b`: consumidor RabbitMQ e SMTP.
- `frontend`: HTML/CSS/JS.
- `nginx`: reverse proxy.
- `compose.yml`: containers e rede.

## Endpoints
`GET /api/health`
`POST /api/auth/register` JSON: `{"name":"Ana","email":"ana@example.com","password":"SenhaForte123!"}`
`POST /api/auth/login` JSON: `{"email":"ana@example.com","password":"SenhaForte123!"}`

## Importante
Este é um ponto de partida educacional, não uma configuração de produção. Login ainda não cria sessão persistente nem token; faltam rate limiting, recuperação/confirmação de conta, testes, monitoramento e transactional outbox para garantir publicação mesmo se o broker cair entre salvar usuário e publicar evento. SQLite é para desenvolvimento; migre para PostgreSQL antes de escalar o Serviço A em múltiplas réplicas. Kubernetes e HPA são etapas posteriores do PDF.
