# Microservices on Kubernetes

A two-cluster Kubernetes setup. Cluster 1 runs the application and its own monitoring stack. Cluster 2 acts as the central observability cluster, aggregating metrics from all clusters into a single place.

---

## Cluster 1 — Application & Monitoring

3 VMs: 1 control plane, 2 worker nodes.

Runs a simple event-driven microservices application alongside a full monitoring stack.

### Application Stack
```
Browser
└── Frontend (Flask)
    └── Backend (Node.js)
        ├── PostgreSQL (persistent storage)
        │    └── PgAdmin (database management)
        └── Kafka (event streaming)
            └── Worker (Node.js Kafka consumer)
                └── Redis (processed events & counters)

### Data Flow

1. User submits a registration via the frontend.
2. Backend writes the user record to PostgreSQL.
3. Backend produces a `user_created` event to a Kafka topic.
4. Worker consumes the event and updates Redis:
   - increments counters
   - pushes the event to the recent events feed
5. Frontend polls the backend for statistics and events, displaying live data without page reloads.

### Monitoring Stack

Deployed via kube-prometheus-stack helm chart.

├── Prometheus + Thanos Sidecar
│   ├── Kubernetes cluster metrics
│   ├── Node metrics
│   ├── Container metrics
│   └── PostgreSQL exporter

The Thanos Sidecar runs alongside Prometheus, uploading metric blocks to S3 every 2 hours
and exposing a gRPC endpoint for the Cluster 2 Querier to query live metrics.
```
---

## Cluster 2 — Central Observability

1 VM: single-node cluster.

Runs its own Prometheus for self-monitoring, plus the central Thanos stack that aggregates
metrics from all clusters.

### Monitoring Stack
```
├── Prometheus + Thanos Sidecar
│   ├── Kubernetes cluster metrics
│   └── Node metrics
│
├── Thanos Stack (bitnami/thanos helm chart)
│   ├── Querier         — federates live metrics from all cluster sidecars via gRPC
│   ├── Store Gateway   — serves historical metrics from S3
│   └── Compactor       — compacts and downsamples blocks in S3
│
└── Grafana             — central dashboards, pointed at Thanos Querier as datasource

### Object Storage

└── AWS S3 — shared across all clusters, long-term metrics retention

Prometheus blocks are uploaded by each cluster's Thanos Sidecar. The Store Gateway reads
from this bucket to serve historical data. The Compactor runs against it periodically to
reduce storage cost and improve query performance.
```
---

## Repository Structure

**Kubernetes/cluster1/**
Manifests and Helm chart values for Cluster 1 — application deployments, kube-prometheus-stack config, and Thanos sidecar configuration.

**Kubernetes/cluster2/**
Manifests and Helm chart values for Cluster 2 — bitnami/thanos deployment and Prometheus self-monitoring config.

**LocalDevelopment/**
Service source code and Docker Compose setups for local testing:
- Backend service
- Frontend service
- Worker service
- Redis
- Kafka

**ClusterSetup/**
Notes and scripts for setting up Kubernetes clusters using `kubeadm`.