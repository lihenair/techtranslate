---
source_url: https://medium.com/@PlatformEnthusiast/architecting-observability-a-complete-guide-to-otel-and-loki-integration-23b77109c44f
fetched_at: 2026-09-02T02:23:42Z
fetch_method: jina
issue: 186
title_zh: 可观测性架构：OpenTelemetry 与 Loki 集成完整指南
tech_domain: devops
---

# Architecting Observability: A Complete Guide to OTel and Loki Integration

[![Image 1: The Platform Enthusiast](https://miro.medium.com/v2/resize:fill:32:32/1*KrEZY_J6WX01zBTy_xxFTA.png)](https://medium.com/@PlatformEnthusiast?source=post_page---byline--23b77109c44f---------------------------------------)

9 min read

Feb 16, 2026

There are numerous tools available for implementing observability in Kubernetes. In modern distributed systems, achieving comprehensive observability requires correlating traces, metrics, and logs to understand application behavior and troubleshoot issues effectively. One tool which essentials act as a collector and open source is Otel.

Press enter or click to view image in full size

![Image 2](https://miro.medium.com/v2/resize:fit:700/1*z56pdyjWXyhlmPh8EDNzRg.png)

AI generated images OTEL & Loki

OpenTelemetry (OTel) has emerged as the industry-standard instrumentation framework for collecting distributed traces and metrics, while Grafana Loki provides a horizontally scalable, cost-efficient log aggregation system designed specifically for cloud-native environments. This guide explores how to architect a unified observability stack by integrating OpenTelemetry’s rich telemetry collection capabilities with Loki’s efficient log storage and querying.

Before starting this guide, make sure you have kubernetes cluster running and cluster access to pull images fromthe internet. We will install OTel & Grafana Loki. You will begin by installing OTel in kubernetes. First create otel-server.yaml.

mode: daemonset

image:

 repository: otel/opentelemetry-collector-contrib

 

resources:

 limits:

 cpu: 500m

 memory: 512Mi

 requests:

 cpu: 200m

 memory: 256Mi

service:

 type: NodePort
ports:

 otlp:

 enabled: true

 containerPort: 4317

 servicePort: 4317

 nodePort: 30317

 protocol: TCP

 appProtocol: grpc

 otlp-http:

 enabled: true

 containerPort: 4318

 servicePort: 4318

 nodePort: 30318

 protocol: TCP

 metrics:

 enabled: true

 containerPort: 8888

 servicePort: 8888

 protocol: TCP

config:

 receivers:

 otlp:

 protocols:

 grpc:

 endpoint: 0.0.0.0:4317

 http:

 endpoint: 0.0.0.0:4318

 processors:

 

 batch:

 timeout: 10s

 send_batch_size: 1024

 

 memory_limiter:

 check_interval: 5s

 limit_mib: 400

 spike_limit_mib: 100

 

 resourcedetection:

 detectors: [env, system]

 timeout: 5s

 

 k8sattributes:

 auth_type: "serviceAccount"

 passthrough: false

 filter:

 node_from_env_var: KUBE_NODE_NAME

 extract:

 metadata:

 - k8s.pod.name 

 - k8s.pod.uid

 - k8s.namespace.name

 - k8s.node.name

 - k8s.container.name

 labels:

 - tag_name: app

 key: app

 pod_association:

 - sources:

 - from: resource_attribute

 name: k8s.pod.name

 - from: resource_attribute

 name: k8s.namespace.name

 - sources:

 - from: resource_attribute

 name: k8s.pod.ip

 - sources:

 - from: resource_attribute

 name: k8s.pod.uid

 - sources:

 - from: connection

 

 resource:

 attributes:

 - key: namespace

 from_attribute: k8s.namespace.name

 action: insert

 - key: pod

 from_attribute: k8s.pod.name

 action: insert

 - key: container

 from_attribute: k8s.container.name

 action: insert 

 

 attributes:

 actions:

 - key: environment

 value: non-production

 action: insert

 exporters:

 

 prometheus:

 endpoint: "0.0.0.0:8889"

 namespace: otel

 const_labels:

 environment: nonprod

 

 prometheusremotewrite:

 endpoint: http://prometheus-server.monitoring.svc.cluster.local/api/v1/write

 tls:

 insecure: true

 

 otlphttp/loki:

 endpoint: http://loki-gateway.monitoring.svc.cluster.local/otlp

 tls:

 insecure: true

 

 sending_queue:

 enabled: true

 queue_size: 5000

 retry_on_failure:

 enabled: true

 initial_interval: 5s

 max_elapsed_time: 300s

service:

 pipelines:

 

 traces:

 receivers: [otlp]

 processors: [memory_limiter, resourcedetection, attributes, batch]

 exporters: [debug]

 

 metrics:

 receivers: [otlp, prometheus, hostmetrics]

 processors: [memory_limiter, resourcedetection, attributes, batch]

 exporters: [prometheus, prometheusremotewrite, debug]

 

 logs:

 receivers: [otlp, filelog]

 processors: [memory_limiter, k8sattributes, resource, resourcedetection, attributes, batch]

 exporters: [otlphttp/loki, debug]

clusterRole:

 create: true

 rules:

 - apiGroups: [""]

 resources: ["pods", "namespaces", "nodes"]

 verbs: ["get", "list", "watch"]

 - apiGroups: ["apps"]

 resources: ["replicasets"]

 verbs: ["get", "list", "watch"]

 - apiGroups: ["extensions"]

 resources: ["replicasets"]

 verbs: ["get", "list", "watch"]

serviceAccount:

 create: true

 name: otel-collector

podSecurityContext:

 runAsUser: 0

 runAsGroup: 0

 fsGroup: 0

extraVolumes:

 - name: varlogpods

 hostPath:

 path: /var/log/pods

 - name: varlibdockercontainers

 hostPath:

 path: /var/lib/docker/containers

extraVolumeMounts:

 - name: varlogpods

 mountPath: /var/log/pods

 readOnly: true

 - name: varlibdockercontainers

 mountPath: /var/lib/docker/containers

 readOnly: true

autoscaling:

 enabled: false

Key takeaways:

1.   OTel will be deployed as a daemonset in kubernetes cluster
2.   In the OpenTelemetry collector configuration, it is divided into several points: Receivers (The “Inputs”), Processors (The “Cleaning & Enrichment”), Exporters (The “Outputs”), Service / Pipelines (The “Wiring”). we will explain each function of this config in next section
3.   ClusterRole section is a part of Kubernetes RBAC (Role-Based Access Control). It is essentially a “permission slip” that tells the Kubernetes API what the OpenTelemetry Collector is allowed to see and do.
4.   Autoscalling section to manage the pod autoscalling for OTel

The OpenTelemetry (OTel) Collector acts as a central data pipeline. It sits between your applications and your monitoring tools (Prometheus and Loki), handling the “heavy lifting” of data collection, cleaning, and delivery.

The configuration is organized into four main sections that represent the flow of data:

### 1. Receivers (The “Inputs”)

These define where data comes from. In your setup, the collector listens for:

1.   otlp: Data sent directly from your apps using the OpenTelemetry SDK.
2.   hostmetrics: Hardware stats like CPU, RAM, and Disk directly from the Kubernetes node.
3.   filelog: Tailing the raw log files in /var/log/pods/. We added a specific Regex Parser here to extract the namespace and pod name from the file path so you can filter logs easily.

### 2. Processors (The “Cleaning & Enrichment”)

This is where the magic happens. Before sending data out, the collector modifies it:

1.   k8sattributes: The most important one for you. It talks to the Kubernetes API to find out which pod a log or metric belongs to, adding labels like pod_name and namespace.
2.   resource: We used this to create “shortcuts” for Loki labels, transforming complex metadata into simple keys like {pod=”my-app”}.
3.   batch: It waits until it has a “batch” of data (e.g., 8192 entries or 200ms) before sending it. This is much more efficient than sending every single log line one by one.
4.   memory_limiter: A safety net. If the collector uses too much RAM, it will drop data instead of crashing your node.

### 3. Exporters (The “Outputs”)

These define where data goes:

1.   prometheusremotewrite: Pushes metrics to your Prometheus server.
2.   otlphttp/loki: Pushes logs to your Loki instance. We added a sending_queue here to handle network glitches.
3.   debug: Prints the data to the collector’s own console logs — very useful when you aren’t sure why a log isn’t showing up in Grafana.

### 4. Service / Pipelines (The “Wiring”)

This section connects everything. It defines the path for each data type:

*   Metrics Pipeline: Receivers (OTLP, hostmetrics) → Processors → Exporters (Prometheus).
*   Logs Pipeline: Receivers (OTLP, filelog) → Processors → Exporters (Loki).

Without this configuration, your logs and metrics would be “blind.” They wouldn’t have labels, they wouldn’t be compressed, and they would be much harder to query. This configuration turns raw text and numbers into structured, searchable observability data.

## Get The Platform Enthusiast’s stories in your inbox

Join Medium for free to get updates from this writer.

Remember me for faster sign in

Continue copy and paste yaml file above, then helm install it use these command

helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts

helm repo update
kubectl create namespace monitoring

helm install otel-collector open-telemetry/opentelemetry-collector \

 -f otel-server.yaml \

 --namespace monitoring

After the installation success, make sure the OTel pod is running. second you will continue to install grafana and prometheus. Create two yaml files: prometheus.yaml & grafana.yaml

server:

 service:

 type: NodePort

 nodePort: 30090
extraFlags:

 - web.enable-remote-write-receiver

 - web.enable-lifecycle

persistentVolume:

 enabled: true

 size: 4Gi

 storageClass: "" 

 

 retention: 15d

global:

 scrape_interval: 15s

 evaluation_interval: 15s

nodeExporter:

 enabled: true

kubeStateMetrics:

 enabled: true

Press enter or click to view image in full size

![Image 3](https://miro.medium.com/v2/resize:fit:700/1*xNqE7lQWW07ZqNjZyuVV5w.png)

Key Takeaway explanation of script prometheus.yaml

service:

 type: NodePort

 nodePort: 30085
persistence:

 enabled: true

 type: pvc

 size: 2Gi

initChownData:

 enabled: false

podSecurityContext:

 fsGroup: 472

 runAsGroup: 472

 runAsUser: 472

containerSecurityContext:

 runAsUser: 472

 runAsGroup: 472

 allowPrivilegeEscalation: false

 readOnlyRootFilesystem: false

adminUser: admin

datasources:

 datasources.yaml:

 apiVersion: 1

 datasources:

 - name: Prometheus

 type: prometheus

 url: http://prometheus-server.monitoring.svc.cluster.local 

 access: proxy

 isDefault: true

 - name: Loki

 type: loki

 url: http://loki-gateway.monitoring.svc.cluster.local

 access: proxy

dashboardProviders:

 dashboardproviders.yaml:

 apiVersion: 1

 providers:

 - name: 'default'

 orgId: 1

 folder: ''

 type: file

 disableDeletion: false

 editable: true

 options:

 path: /var/lib/grafana/dashboards/default

dashboards:

 default:

 node-exporter-full:

 gnetId: 1860 

 revision: 37

 datasource: Prometheus

 kubernetes-pods:

 gnetId: 6417 

 revision: 1

 datasource: Prometheus

grafana.ini:

 server:

 protocol: http

 domain: <domain grafana>

 root_url: http://<domain grafana>/ 

 security:

 allow_embedding: true

 cookie_samesite: lax

 auth.anonymous:

 enabled: false

Press enter or click to view image in full size

![Image 4](https://miro.medium.com/v2/resize:fit:700/1*FMUtsh0qf1miT5zwCVrKEg.png)

Key Takeaway explanation of script grafana.yaml

Continue copy and paste yaml file above, then helm install it use these command

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm repo add grafana https://grafana.github.io/helm-charts

helm repo update
helm install grafana grafana/grafana \

 -f grafana.yaml \

 --namespace monitoring

helm install prometheus prometheus-community/prometheus \

 -f prometheus.yaml \

 --namespace monitoring

Make sure the pod is running and test access grafana on your browser input url http://<server ip address>:30085/login

Press enter or click to view image in full size

![Image 5](https://miro.medium.com/v2/resize:fit:700/1*ZDXTLYsm3y3DzzLon5F0Wg.png)

grafana login page

Login to grafana use username: admin and password: strongpassword.

After that you can continue install loki.yaml. Create yaml file with the following snippet

deploymentMode: SingleBinary
singleBinary:

 replicas: 1

resources:

 limits:

 cpu: 500m

 memory: 512Mi

 requests:

 cpu: 200m

 memory: 256Mi

persistence:

 enabled: true

 size: 5Gi

 storageClass: ""

loki:

 auth_enabled: false

commonConfig:

 replication_factor: 1

storage:

 type: 'filesystem'

schemaConfig:

 configs:

 - from: 2024-01-01

 store: tsdb

 object_store: filesystem

 schema: v13

 index:

 prefix: loki_index_

 period: 24h

limits_config:

 retention_period: 168h 

 max_query_series: 1000

 max_query_parallelism: 16

 ingestion_rate_mb: 10

 ingestion_burst_size_mb: 20

 per_stream_rate_limit: 5MB

 per_stream_rate_limit_burst: 10MB

compactor:

 retention_enabled: true

 delete_request_store: filesystem

 retention_delete_delay: 2h

 retention_delete_worker_count: 150

service:

 type: NodePort

 port: 3100

 nodePort: 30100

gateway:

 enabled: true

 replicas: 1

service:

 type: NodePort

 port: 80

 nodePort: 30101

resources:

 limits:

 cpu: 200m

 memory: 256Mi

 requests:

 cpu: 100m

 memory: 128Mi

monitoring:

 selfMonitoring:

 enabled: false

 grafanaAgent:

 installOperator: false

lokiCanary:

 enabled: false

test:

 enabled: false

backend:

 replicas: 0

read:

 replicas: 0

write:

 replicas: 0

chunksCache:

 enabled: false

resultsCache:

 enabled: false

Press enter or click to view image in full size

![Image 6](https://miro.medium.com/v2/resize:fit:700/1*7UExZlqr-fe11nlQ7jwA5w.png)

Core configuration for loki.yaml

Press enter or click to view image in full size

![Image 7](https://miro.medium.com/v2/resize:fit:700/1*jfaW36mk-yTajEIQY_0A0w.png)

Data retention setup in loki.yaml

Press enter or click to view image in full size

![Image 8](https://miro.medium.com/v2/resize:fit:700/1*S6_HjLqKtryUcflTnd9oCg.png)

service and gateway setup in loki.yaml

Continue to copy and paste yaml file above, then helm install it using these commands and make surethe pod is running

helm install loki grafana/loki -f loki.yaml -n monitoring
To access Grafana Loki, you can go to explore, then choose Loki as a source

Press enter or click to view image in full size

![Image 9](https://miro.medium.com/v2/resize:fit:700/1*xj6XnZvyAORP6HKDSxvAtA.png)

Then you can start a query by select label, then click the blue button refresh to run the query. Congratulations, you have setup grafana loki and Otel for pod monitoring in kubernetes.

Press enter or click to view image in full size

![Image 10](https://miro.medium.com/v2/resize:fit:700/1*DK9MG0QVcQ8k3s7uGMfjmw.png)

Sample query in Grafana Loki

Press enter or click to view image in full size

![Image 11](https://miro.medium.com/v2/resize:fit:700/1*mPn8pf_v3QwTxcnSOzWOLQ.png)

Sample log from logger service
