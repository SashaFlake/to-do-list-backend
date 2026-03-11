#!/usr/bin/env python3
"""
Production-ready FastAPI project structure generator
Creates a complete backend project with database, cache, and Helm configuration
"""

import os
from pathlib import Path

def create_file(path: Path, content: str = ""):
    """Create a file with given content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {path}")

def create_directory(path: Path):
    """Create a directory"""
    path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {path}")

# Base project directory
PROJECT_NAME = "fastapi-app"
BASE_DIR = Path(PROJECT_NAME)

print(f"\n🚀 Creating production-ready FastAPI project: {PROJECT_NAME}\n")

# Main application structure
APP_DIR = BASE_DIR / "app"

# Create __init__.py files
create_file(APP_DIR / "__init__.py", "")
create_file(APP_DIR / "api" / "__init__.py", "")
create_file(APP_DIR / "api" / "v1" / "__init__.py", "")
create_file(APP_DIR / "core" / "__init__.py", "")
create_file(APP_DIR / "db" / "__init__.py", "")
create_file(APP_DIR / "models" / "__init__.py", "")
create_file(APP_DIR / "schemas" / "__init__.py", "")
create_file(APP_DIR / "services" / "__init__.py", "")
create_file(APP_DIR / "repositories" / "__init__.py", "")

# main.py
create_file(APP_DIR / "main.py", """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.session import init_db, close_db
from app.core.cache import init_cache, close_cache

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    await init_db()
    await init_cache()
    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    await close_cache()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
""")

# core/config.py
create_file(APP_DIR / "core" / "config.py", """from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "FastAPI Application"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Database pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis cache TTL
    CACHE_TTL: int = 300

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
""")

# core/logging.py
create_file(APP_DIR / "core" / "logging.py", """import logging
import sys
from app.core.config import settings


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(settings.PROJECT_NAME)
""")

# core/cache.py
create_file(APP_DIR / "core" / "cache.py", """import redis.asyncio as redis
from typing import Optional
import json
from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


async def init_cache():
    global _redis_client
    _redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True
    )
    await _redis_client.ping()


async def close_cache():
    global _redis_client
    if _redis_client:
        await _redis_client.close()


def get_redis() -> redis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis not initialized")
    return _redis_client


class CacheService:
    def __init__(self):
        self.redis = get_redis()

    async def get(self, key: str) -> Optional[dict]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: dict, ttl: int = settings.CACHE_TTL):
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key) > 0
""")

# db/session.py
create_file(APP_DIR / "db" / "session.py", """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
""")

# models/user.py (example model)
create_file(APP_DIR / "models" / "user.py", """from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""")

# schemas/user.py
create_file(APP_DIR / "schemas" / "user.py", """from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
""")

# repositories/user.py
create_file(APP_DIR / "repositories" / "user.py", """from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, user: UserCreate, hashed_password: str) -> User:
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        await self.db.flush()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        await self.db.flush()
        await self.db.refresh(db_user)
        return db_user

    async def delete(self, user_id: int) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return False

        await self.db.delete(db_user)
        return True
""")

# services/user.py
create_file(APP_DIR / "services" / "user.py", """from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import Optional

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.cache import CacheService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
        self.cache = CacheService()

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, user: UserCreate) -> UserResponse:
        hashed_password = self._hash_password(user.password)
        db_user = await self.repository.create(user, hashed_password)
        return UserResponse.model_validate(db_user)

    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        # Try cache first
        cache_key = f"user:{user_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return UserResponse(**cached)

        # Get from DB
        db_user = await self.repository.get_by_id(user_id)
        if db_user:
            user_response = UserResponse.model_validate(db_user)
            # Cache result
            await self.cache.set(cache_key, user_response.model_dump(mode='json'))
            return user_response
        return None

    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        if user_update.password:
            user_update.password = self._hash_password(user_update.password)

        db_user = await self.repository.update(user_id, user_update)
        if db_user:
            # Invalidate cache
            await self.cache.delete(f"user:{user_id}")
            return UserResponse.model_validate(db_user)
        return None

    async def delete_user(self, user_id: int) -> bool:
        result = await self.repository.delete(user_id)
        if result:
            await self.cache.delete(f"user:{user_id}")
        return result
""")

# api/v1/endpoints/users.py
create_file(APP_DIR / "api" / "v1" / "endpoints" / "__init__.py", "")
create_file(APP_DIR / "api" / "v1" / "endpoints" / "users.py", """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    return await service.create_user(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    user = await service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    result = await service.delete_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
""")

# api/v1/router.py
create_file(APP_DIR / "api" / "v1" / "router.py", """from fastapi import APIRouter
from app.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
""")

# requirements.txt
create_file(BASE_DIR / "requirements.txt", """fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
redis==5.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
""")

# Dockerfile
create_file(BASE_DIR / "Dockerfile", """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

# .dockerignore
create_file(BASE_DIR / ".dockerignore", """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.pytest_cache
.hypothesis
*.md
""")

# Helm chart structure
HELM_DIR = BASE_DIR / "helm" / PROJECT_NAME

# Chart.yaml
create_file(HELM_DIR / "Chart.yaml", f"""apiVersion: v2
name: {PROJECT_NAME}
description: A production-ready FastAPI application with PostgreSQL and Redis
type: application
version: 1.0.0
appVersion: "1.0.0"
""")

# values.yaml
create_file(HELM_DIR / "values.yaml", """replicaCount: 2

image:
  repository: your-registry/fastapi-app
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: false
  allowPrivilegeEscalation: false

service:
  type: ClusterIP
  port: 80
  targetPort: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: fastapi-tls
      hosts:
        - api.example.com

resources:
  limits:
    cpu: 1000m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

nodeSelector: {}

tolerations: []

affinity: {}

# Application configuration
config:
  projectName: "FastAPI Application"
  version: "1.0.0"
  apiV1Str: "/api/v1"
  secretKey: "your-secret-key-change-in-production"
  algorithm: "HS256"
  accessTokenExpireMinutes: 30
  allowedOrigins: "*"
  dbPoolSize: 20
  dbMaxOverflow: 10
  dbPoolTimeout: 30
  cacheTtl: 300

# PostgreSQL configuration
postgresql:
  enabled: true
  auth:
    username: fastapi
    password: fastapi-password
    database: fastapi_db
  primary:
    persistence:
      enabled: true
      size: 10Gi
    resources:
      requests:
        memory: 256Mi
        cpu: 250m
      limits:
        memory: 512Mi
        cpu: 500m

# Redis configuration
redis:
  enabled: true
  auth:
    enabled: true
    password: redis-password
  master:
    persistence:
      enabled: true
      size: 5Gi
    resources:
      requests:
        memory: 128Mi
        cpu: 100m
      limits:
        memory: 256Mi
        cpu: 250m
""")

# templates/deployment.yaml
create_file(HELM_DIR / "templates" / "deployment.yaml", """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "fastapi-app.fullname" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "fastapi-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "fastapi-app.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "fastapi-app.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.service.targetPort }}
          protocol: TCP
        env:
        - name: PROJECT_NAME
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: project-name
        - name: VERSION
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: version
        - name: API_V1_STR
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: api-v1-str
        - name: POSTGRES_HOST
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: postgres-host
        - name: POSTGRES_PORT
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: postgres-port
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: postgres-user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: postgres-password
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: postgres-db
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: redis-host
        - name: REDIS_PORT
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: redis-port
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: redis-password
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: secret-key
        - name: ALGORITHM
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: algorithm
        - name: ACCESS_TOKEN_EXPIRE_MINUTES
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: access-token-expire-minutes
        - name: ALLOWED_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: allowed-origins
        - name: DB_POOL_SIZE
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: db-pool-size
        - name: DB_MAX_OVERFLOW
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: db-max-overflow
        - name: DB_POOL_TIMEOUT
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: db-pool-timeout
        - name: CACHE_TTL
          valueFrom:
            configMapKeyRef:
              name: {{ include "fastapi-app.fullname" . }}
              key: cache-ttl
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 12 }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 12 }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
""")

# templates/service.yaml
create_file(HELM_DIR / "templates" / "service.yaml", """apiVersion: v1
kind: Service
metadata:
  name: {{ include "fastapi-app.fullname" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "fastapi-app.selectorLabels" . | nindent 4 }}
""")

# templates/configmap.yaml
create_file(HELM_DIR / "templates" / "configmap.yaml", """apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "fastapi-app.fullname" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
data:
  project-name: {{ .Values.config.projectName | quote }}
  version: {{ .Values.config.version | quote }}
  api-v1-str: {{ .Values.config.apiV1Str | quote }}
  postgres-host: {{ include "fastapi-app.fullname" . }}-postgresql
  postgres-port: "5432"
  postgres-db: {{ .Values.postgresql.auth.database | quote }}
  redis-host: {{ include "fastapi-app.fullname" . }}-redis-master
  redis-port: "6379"
  algorithm: {{ .Values.config.algorithm | quote }}
  access-token-expire-minutes: {{ .Values.config.accessTokenExpireMinutes | quote }}
  allowed-origins: {{ .Values.config.allowedOrigins | quote }}
  db-pool-size: {{ .Values.config.dbPoolSize | quote }}
  db-max-overflow: {{ .Values.config.dbMaxOverflow | quote }}
  db-pool-timeout: {{ .Values.config.dbPoolTimeout | quote }}
  cache-ttl: {{ .Values.config.cacheTtl | quote }}
""")

# templates/secret.yaml
create_file(HELM_DIR / "templates" / "secret.yaml", """apiVersion: v1
kind: Secret
metadata:
  name: {{ include "fastapi-app.fullname" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
type: Opaque
data:
  postgres-user: {{ .Values.postgresql.auth.username | b64enc | quote }}
  postgres-password: {{ .Values.postgresql.auth.password | b64enc | quote }}
  redis-password: {{ .Values.redis.auth.password | b64enc | quote }}
  secret-key: {{ .Values.config.secretKey | b64enc | quote }}
""")

# templates/ingress.yaml
create_file(HELM_DIR / "templates" / "ingress.yaml", """{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "fastapi-app.fullname" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "fastapi-app.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
""")

# templates/hpa.yaml
create_file(HELM_DIR / "templates" / "hpa.yaml", """{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "fastapi-app.fullname" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "fastapi-app.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
""")

# templates/_helpers.tpl
create_file(HELM_DIR / "templates" / "_helpers.tpl", """{{/*
Expand the name of the chart.
*/}}
{{- define "fastapi-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "fastapi-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "fastapi-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "fastapi-app.labels" -}}
helm.sh/chart: {{ include "fastapi-app.chart" . }}
{{ include "fastapi-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "fastapi-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fastapi-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "fastapi-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "fastapi-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
""")

# templates/serviceaccount.yaml
create_file(HELM_DIR / "templates" / "serviceaccount.yaml", """{{- if .Values.serviceAccount.create -}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "fastapi-app.serviceAccountName" . }}
  labels:
    {{- include "fastapi-app.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
""")

# .env.example
create_file(BASE_DIR / ".env.example", """# Application
PROJECT_NAME=FastAPI Application
VERSION=1.0.0
API_V1_STR=/api/v1

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=fastapi
POSTGRES_PASSWORD=fastapi-password
POSTGRES_DB=fastapi_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis-password
REDIS_DB=0

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=*

# Database pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Cache
CACHE_TTL=300
""")

# docker-compose.yml for local development
create_file(BASE_DIR / "docker-compose.yml", """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-fastapi}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-fastapi-password}
      POSTGRES_DB: ${POSTGRES_DB:-fastapi_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis-password}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
""")

# README.md
create_file(BASE_DIR / "README.md", f"""# {PROJECT_NAME}

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
{PROJECT_NAME}/
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
│   └── {PROJECT_NAME}/
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

3. Update values in `helm/{PROJECT_NAME}/values.yaml`:
- Set your container registry
- Configure ingress hostname
- Update secrets (SECRET_KEY, passwords)

4. Install the chart:
```bash
helm install {PROJECT_NAME} ./helm/{PROJECT_NAME} \
  --namespace fastapi-app \
  --create-namespace
```

5. Check deployment:
```bash
kubectl get pods -n fastapi-app
kubectl get svc -n fastapi-app
kubectl get ingress -n fastapi-app
```

### Upgrade deployment

```bash
helm upgrade {PROJECT_NAME} ./helm/{PROJECT_NAME} \
  --namespace fastapi-app
```

### Uninstall

```bash
helm uninstall {PROJECT_NAME} --namespace fastapi-app
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
- `GET /api/v1/users/{{user_id}}` - Get user (with caching)
- `PUT /api/v1/users/{{user_id}}` - Update user
- `DELETE /api/v1/users/{{user_id}}` - Delete user

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
""")

# Makefile
create_file(BASE_DIR / "Makefile", """.PHONY: help install dev run test docker-build docker-up docker-down helm-install helm-upgrade helm-uninstall

help:
	@echo "Available commands:"
	@echo "  install        Install dependencies"
	@echo "  dev            Run development server"
	@echo "  test           Run tests"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-up      Start Docker Compose"
	@echo "  docker-down    Stop Docker Compose"
	@echo "  helm-install   Install Helm chart"
	@echo "  helm-upgrade   Upgrade Helm chart"
	@echo "  helm-uninstall Uninstall Helm chart"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

docker-build:
	docker build -t fastapi-app:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

helm-install:
	helm install fastapi-app ./helm/fastapi-app --namespace fastapi-app --create-namespace

helm-upgrade:
	helm upgrade fastapi-app ./helm/fastapi-app --namespace fastapi-app

helm-uninstall:
	helm uninstall fastapi-app --namespace fastapi-app
""")

# .gitignore
create_file(BASE_DIR / ".gitignore", """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Database
*.db
*.sqlite

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
*.tar
""")

print(f"\n✅ Project structure created successfully!\n")
print(f"📁 Project directory: {PROJECT_NAME}/\n")
print("Next steps:")
print(f"  1. cd {PROJECT_NAME}")
print("  2. cp .env.example .env")
print("  3. docker-compose up -d")
print("  4. Open http://localhost:8000/api/v1/docs\n")
print("For Kubernetes deployment:")
print("  1. Update helm/fastapi-app/values.yaml")
print("  2. helm repo add bitnami https://charts.bitnami.com/bitnami")
print("  3. helm install fastapi-app ./helm/fastapi-app --namespace fastapi-app --create-namespace\n")
