# Microservices on Kubernetes

A simple event-driven microservices application deployed on Kubernetes.

---

## Data Flow

1. User submits a registration via the frontend.
2. Backend writes the user record to PostgreSQL.
3. Backend produces a `user_created` event to a Kafka topic.
4. Worker consumes the event and updates Redis:
   - increments counters
   - pushes the event to the recent events feed
5. Frontend polls the backend for statistics and events, displaying live data without page reloads.


## Current Architecture
```

3 VMs
• 1 Kubernetes control plane
• 2 Kubernetes worker nodes

Application stack running on Kubernetes:

Browser
└── Frontend (Flask)
    └── Backend (Node.js)
        ├── PostgreSQL (persistent storage)
        │    └── PgAdmin (database management)
        └── Kafka (event streaming)
            └── Worker (Node.js Kafka consumer)
                └── Redis (processed events & counters)

Monitoring Layer

├── Prometheus
│   ├── Kubernetes cluster metrics
│   ├── Node metrics
│   ├── Container metrics
│   ├── PostgreSQL exporter
│   └── Kafka exporter
│
└── Grafana
    └── Dashboards visualizing Prometheus metrics

```


---

## Repository Structure

**Kubernetes/**  
Contains Kubernetes manifests and Helm charts used to deploy the application.

**LocalDevelopment/**  
Contains service source code and Docker Compose setups for local testing:
- Backend service
- Frontend service
- Worker service
- Redis
- Kafka

**ClusterSetup/**  
Notes and scripts for setting up the Kubernetes cluster using `kubeadm`.

