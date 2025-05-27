# Docker Setup for SM2AF

This document provides information about the Docker setup for the Sheet Music to Audio File (SM2AF) application.

## Architecture

The Docker setup consists of two main services:

1. **Backend Service**: A FastAPI application that handles the sheet music processing
2. **Frontend Service**: A React application that provides the user interface

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Building and running your application

When you're ready, start your application by running:
```bash
docker compose up --build -d
```

Your application will be available at:
- Web Interface: http://localhost
- API: http://localhost:8000

## Service Details

### Backend Service

- **Base Image**: Python 3.12.4 slim
- **Exposed Port**: 8000
- **Dependencies**: FluidSynth, TiMidity, and other Python packages
- **Volumes**: The uploads directory is mounted for persistence

### Frontend Service

- **Base Image**: Node.js for building, NGINX for serving
- **Exposed Port**: 80
- **Build Process**: Two-stage build for optimized production deployment

## Development with Docker

For development purposes, you can mount your source code directories:

```yaml
services:
  backend:
    volumes:
      - ./src:/app/src
      - ./main.py:/app/main.py
  
  frontend:
    volumes:
      - ./frontEnd/src:/app/src
```

Add these to the `compose.yaml` file and restart the services.

## Deploying your application to the cloud

First, build your images:
```bash
docker compose build
```

If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the images for that platform:
```bash
docker buildx build --platform=linux/amd64 -t myregistry.com/sm2af-backend -f dockerfile.backend .
docker buildx build --platform=linux/amd64 -t myregistry.com/sm2af-frontend -f frontEnd/dockerfile.frontend frontEnd
```

Then, push them to your registry:
```bash
docker push myregistry.com/sm2af-backend
docker push myregistry.com/sm2af-frontend
```

## References
* [Docker's Python guide](https://docs.docker.com/language/python/)
* [Docker's NodeJS guide](https://docs.docker.com/language/nodejs/)
* [Docker Compose reference](https://docs.docker.com/compose/compose-file/compose-file-v3/)