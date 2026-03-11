# fastapi-app

Production-ready FastAPI application with PostgreSQL and Redis.

## Features

- ✅ FastAPI with async/await support
- ✅ PostgreSQL with SQLAlchemy 2.0 and asyncpg
- ✅ Redis caching layer
- ✅ Repository pattern
- ✅ Service layer
- ✅ Pydantic v2 schemas
- ✅ Docker and Docker Compose
- ✅ Kubernetes deployment with Helm
- ✅ Configuration from Helm values
- ✅ Health checks and probes
- ✅ Horizontal Pod Autoscaling
- ✅ Production-ready structure

## Project Structure

```
fastapi-app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── users.py
│   │       └── router.py
│   ├── core/
│   │   ├── cache.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   └── user.py
│   ├── repositories/
│   │   └── user.py
│   ├── schemas/
│   │   └── user.py
│   ├── services/
│   │   └── user.py
│   └── main.py
├── helm/
│   └── fastapi-app/
│       ├── templates/
│       ├── Chart.yaml
│       └── values.yaml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Local Development

### Prerequisites

- Python 3.11+
- Docker and Docker Compose

### Setup

1. Copy environment variables:
```bash
cp .env.example .env
```

2. Start services with Docker Compose:
```bash
docker-compose up -d
```

3. Access the API:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs
- Health: http://localhost:8000/health

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster
- Helm 3
- kubectl configured

### Deploy with Helm

1. Add Bitnami repository for PostgreSQL and Redis:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

2. Create namespace:
```bash
kubectl create namespace fastapi-app
```

3. Update values in `helm/fastapi-app/values.yaml`:
- Set your container registry
- Configure ingress hostname
- Update secrets (SECRET_KEY, passwords)

4. Install the chart:
```bash
helm install fastapi-app ./helm/fastapi-app   --namespace fastapi-app   --create-namespace
```

5. Check deployment:
```bash
kubectl get pods -n fastapi-app
kubectl get svc -n fastapi-app
kubectl get ingress -n fastapi-app
```

### Upgrade deployment

```bash
helm upgrade fastapi-app ./helm/fastapi-app   --namespace fastapi-app
```

### Uninstall

```bash
helm uninstall fastapi-app --namespace fastapi-app
```

## Configuration

All configuration is managed through Helm values. Key configuration areas:

- **Application**: Project name, version, API prefix
- **Database**: Connection settings, pool configuration
- **Redis**: Connection and cache TTL
- **Security**: Secret keys, CORS settings
- **Resources**: CPU/memory limits and requests
- **Autoscaling**: HPA configuration
- **Ingress**: Domain and TLS settings

## API Endpoints

### Users

- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user (with caching)
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Health

- `GET /health` - Health check endpoint

## Architecture

### Layers

1. **API Layer** (`api/`): FastAPI routers and endpoints
2. **Service Layer** (`services/`): Business logic and caching
3. **Repository Layer** (`repositories/`): Database operations
4. **Model Layer** (`models/`): SQLAlchemy models
5. **Schema Layer** (`schemas/`): Pydantic schemas for validation

### Key Components

- **Database Session**: Async SQLAlchemy with connection pooling
- **Cache Service**: Redis-based caching with TTL
- **Configuration**: Pydantic Settings with environment variables
- **Logging**: Structured logging to stdout

## Development Guidelines

1. **Add new endpoints**: Create in `api/v1/endpoints/` and register in `router.py`
2. **Add models**: Define in `models/` and create corresponding schemas
3. **Business logic**: Implement in `services/` layer
4. **Database operations**: Implement in `repositories/` layer
5. **Configuration**: Add to `core/config.py` and Helm values

## Production Checklist

- [ ] Change all default passwords and secret keys
- [ ] Configure proper ingress with TLS
- [ ] Set appropriate resource limits
- [ ] Configure monitoring and logging
- [ ] Set up backup for PostgreSQL
- [ ] Configure Redis persistence
- [ ] Review security contexts
- [ ] Set up CI/CD pipeline
- [ ] Configure network policies
- [ ] Enable pod security policies

## License

MIT
