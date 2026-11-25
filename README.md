# CRUD Master Py

A microservices movie streaming platform built with **Python 3**, **Flask**, **SQLAlchemy**, **PostgreSQL**, **RabbitMQ**, **pika**, **Vagrant**, **VirtualBox**, and **PM2**.

## Architecture

```
                     Client
                       │
                       ▼
                  API Gateway
             gateway-vm (192.168.56.10:3000)
                 /            \
      HTTP      /              \  RabbitMQ (billing_queue)
               ▼                ▼
        Inventory API       Billing API
  inventory-vm (192.168.56.11)  billing-vm (192.168.56.12)
    http://localhost:8080/        │
               │                  ▼
               ▼             PostgreSQL
          PostgreSQL        (billing_db.orders)
       (movies_db.movies)
```

## Tech Stack

- **Python 3** with **Flask** and **SQLAlchemy**
- **pika** for RabbitMQ publishing and consuming
- **PostgreSQL** (`movies_db` and `billing_db`)
- **RabbitMQ** (`billing_queue`)
- **Vagrant** + **VirtualBox** (three isolated Ubuntu 22.04 VMs)
- **PM2** for process management and resilience testing
- **OpenAPI 3.0** (`openapi.yaml`) and **Postman** (`postman_collection.json`)

## Design Choices

- **Service isolation across VMs**: Each microservice runs in its own VM (`gateway-vm`, `inventory-vm`, `billing-vm`) with its own Python virtual environment (`/opt/venvs/<service>`) managed by PM2.
- **Synchronous vs. Asynchronous communication**: Inventory queries require immediate read/write responses, so `api-gateway-app` proxies `/api/movies` over HTTP. Billing orders use a durable RabbitMQ queue (`billing_queue`) with persistent messages and manual acknowledgments (`basic_ack`) so orders are never lost if `billing-app` is stopped.
- **Centralized configuration**: All ports, hosts, database credentials, and RabbitMQ credentials are stored in `.env` and passed to each VM via `Vagrantfile`. None of the services hardcode credentials.

## Project Structure

```
.
├── .env
├── .gitignore
├── README.md
├── Vagrantfile
├── openapi.yaml
├── postman_collection.json
├── scripts/
│   ├── billing.sh
│   ├── gateway.sh
│   └── inventory.sh
└── srcs/
    ├── api-gateway-app/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── rabbitmq.py
    │   │   └── routes.py
    │   ├── requirements.txt
    │   └── server.py
    ├── billing-app/
    │   ├── app/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── models/
    │   │   │   ├── __init__.py
    │   │   │   └── order.py
    │   │   └── services/
    │   │       ├── __init__.py
    │   │       └── consumer.py
    │   ├── requirements.txt
    │   └── server.py
    └── inventory-app/
        ├── app/
        │   ├── __init__.py
        │   ├── config.py
        │   ├── models/
        │   │   ├── __init__.py
        │   │   └── movie.py
        │   └── routes/
        │       ├── __init__.py
        │       └── movies.py
        ├── requirements.txt
        └── server.py
```

## Environment Variables (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `INVENTORY_HOST` | Bind address for Inventory API | `0.0.0.0` |
| `INVENTORY_PORT` | Port for Inventory API | `8080` |
| `INVENTORY_DB_HOST` | PostgreSQL host for Inventory | `localhost` |
| `INVENTORY_DB_PORT` | PostgreSQL port for Inventory | `5432` |
| `INVENTORY_DB_NAME` | Inventory database name | `movies_db` |
| `INVENTORY_DB_USER` | Inventory database user | `postgres` |
| `INVENTORY_DB_PASSWORD` | Inventory database password | `1312` |
| `BILLING_DB_HOST` | PostgreSQL host for Billing | `localhost` |
| `BILLING_DB_PORT` | PostgreSQL port for Billing | `5432` |
| `BILLING_DB_NAME` | Billing database name | `billing_db` |
| `BILLING_DB_USER` | Billing database user | `postgres` |
| `BILLING_DB_PASSWORD` | Billing database password | `1312` |
| `RABBITMQ_HOST` | RabbitMQ host for API Gateway | `192.168.56.12` |
| `BILLING_RABBITMQ_HOST` | RabbitMQ host for Billing consumer | `localhost` |
| `RABBITMQ_PORT` | RabbitMQ AMQP port | `5672` |
| `RABBITMQ_USER` | RabbitMQ username | `gateway` |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `1312` |
| `RABBITMQ_VHOST` | RabbitMQ virtual host | `/` |
| `RABBITMQ_QUEUE` | Queue name for billing messages | `billing_queue` |
| `GATEWAY_HOST` | Bind address for API Gateway | `0.0.0.0` |
| `GATEWAY_PORT` | Port for API Gateway | `3000` |
| `INVENTORY_API_URL` | Upstream Inventory API URL for Gateway | `http://192.168.56.11:8080` |

## Running with Vagrant

From the project root:

```bash
vagrant up
vagrant status
```

Provisioning automatically installs Python 3, PostgreSQL (`movies_db` and `billing_db`), RabbitMQ (`gateway` user + `billing_queue`), Node.js/PM2, creates virtual environments, and starts all three services via PM2.

Access a VM via SSH:

```bash
vagrant ssh gateway-vm
vagrant ssh inventory-vm
vagrant ssh billing-vm
```

Manage Python processes inside any VM with PM2:

```bash
sudo pm2 list
sudo pm2 stop <app_name>
sudo pm2 start <app_name>
```

Service PM2 app names:
- `api_gateway_app` (on `gateway-vm`)
- `inventory_app` (on `inventory-vm`)
- `billing_app` (on `billing-vm`)

### Provisioning Scripts (`scripts/`)
- [scripts/gateway.sh](scripts/gateway.sh): Installs Python 3 (`venv`/`pip`) and Node.js/PM2, installs `api-gateway-app` dependencies into `/opt/venvs/api-gateway-app`, and starts `api_gateway_app` with PM2.
- [scripts/inventory.sh](scripts/inventory.sh): Installs Python 3, PostgreSQL, and Node.js/PM2, configures the PostgreSQL password and creates `movies_db`, installs `inventory-app` dependencies into `/opt/venvs/inventory-app`, and starts `inventory_app` with PM2.
- [scripts/billing.sh](scripts/billing.sh): Installs Python 3, PostgreSQL, RabbitMQ, and Node.js/PM2, creates `billing_db`, configures the RabbitMQ `gateway` user and permissions, installs `billing-app` dependencies into `/opt/venvs/billing-app`, and starts `billing_app` with PM2.

## Running Locally (Without Vagrant)

Create a virtual environment inside each service directory and run `python server.py` (with local PostgreSQL and RabbitMQ running and `.env` hosts pointing to `localhost`):

```bash
cd srcs/inventory-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Repeat the same steps in `srcs/billing-app` and `srcs/api-gateway-app`.

## API Endpoints & Documentation

OpenAPI specification is provided in [openapi.yaml](openapi.yaml).

- **Inventory API** (`http://localhost:8080/` and proxied via Gateway `http://192.168.56.10:3000`):
  - `GET /api/movies` — Retrieve all movies
  - `GET /api/movies?title=[name]` — Filter movies by title substring
  - `POST /api/movies` — Create a movie (`{"title": "...", "description": "..."}`)
  - `DELETE /api/movies` — Delete all movies
  - `GET /api/movies/<id>` — Retrieve a movie by ID
  - `PUT /api/movies/<id>` — Update a movie by ID
  - `DELETE /api/movies/<id>` — Delete a movie by ID
- **Billing** (via Gateway `http://192.168.56.10:3000/api/billing`):
  - `POST /api/billing` — Queue a billing message to `billing_queue`:

```json
{
  "user_id": "3",
  "number_of_items": "5",
  "total_amount": "180"
}
```

## Testing

1. **Postman**: Import [postman_collection.json](postman_collection.json) into Postman and run the collection to test all Inventory API and API Gateway endpoints.
2. **Billing Queue Resilience**:
   - SSH into `billing-vm` (`vagrant ssh billing-vm`) and stop the consumer:
     ```bash
     sudo pm2 stop billing_app
     ```
   - Send `POST http://192.168.56.10:3000/api/billing` — the gateway still returns `200 OK` (`{"message": "Message posted"}`), while `orders` in `billing_db` is not updated yet.
   - Restart the consumer:
     ```bash
     sudo pm2 start billing_app
     ```
   - All pending messages in `billing_queue` are processed immediately and inserted into `billing_db.orders`.
