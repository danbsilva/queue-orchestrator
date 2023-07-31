# Queue Orchestrator

## Description
<p align="justify">This project is a simple implementation of a queue orchestrator system. It was developed using the Python(Flask) programming language and the KAFKA message broker.</p>

## Services
<p align="justify">The project is composed of the following services:</p>

### FLASK - PYTHON3
- **gateway**: responsible for managing the requests of the users
- **auth**: responsible for managing the authentication of the users
- **automations**: responsible for managing the automations of the users
- **logs**: responsible for managing the logs of the users
- **notifications**: responsible for managing the notifications of the users

## Architecture
<p align="justify">The project is composed of the following architecture:</p>

### POSTGRESQL
- **dbservices**: responsible for managing the database of api-gateway
- **dbusers**: responsible for managing the database of users
- **dbautomations**: responsible for managing the database of automations
- **dblogs**: responsible for managing the database of logs



## Requirements
- Docker

## Installation
<p align="justify">To install the project, you must follow the steps below:</p>

1. Clone the repository
```bash
git clone https://github.com/danbsilva/queue-orchestrator.git
```

2. Enter the project folder
```bash
cd queue-orchestrator
```

3. Execute the Docker Compose
```bash
docker-compose up -d
```
<p align="justify">The command above will create the containers and start the project. The containers created are:</p>

- **zoopkeeper**: responsible for managing the KAFKA cluster
- **kafka**: responsible for managing the KAFKA cluster
- **control-center**: responsible for managing the KAFKA cluster
- **topic-creator**: responsible for creating the topics of the KAFKA cluster
- **redis**: responsible for managing the Redis cluster
- **dbservices**: responsible for managing the database of api-gateway
- **gateway**: responsible for managing the api-gateway
- **dbusers**: responsible for managing the database of users
- **auth**: responsible for managing the authentication service
- **dbautomations**: responsible for managing the database of automations
- **automations**: responsible for managing the automations service
- **dblogs**: responsible for managing the database of logs
- **logs**: responsible for managing the logs service
- **notifications**: responsible for managing the notifications service


# Documentation (Swagger)
<p align="justify">The API Gateway has the following documentation:</p>

```url
http://localhost:2000/api/docs/
```



