---
title: "可观测性架构：OpenTelemetry 与 Loki 集成完整指南"
title_en: "Architecting Observability: A Complete Guide to OTel and Loki Integration"
source_url: https://medium.com/@PlatformEnthusiast/architecting-observability-a-complete-guide-to-otel-and-loki-integration-23b77109c44f
author: The Platform Enthusiast
published_at: 2026-02-16
translated_at: 2026-09-02
tech_domain: devops
tags: [observability, opentelemetry, loki, kubernetes, grafana, prometheus]
cover_image: https://miro.medium.com/v2/resize:fit:700/1*z56pdyjWXyhlmPh8EDNzRg.png
---

# 可观测性架构：OpenTelemetry 与 Loki 集成完整指南

原文链接：<https://medium.com/@PlatformEnthusiast/architecting-observability-a-complete-guide-to-otel-and-loki-integration-23b77109c44f>

原文作者：The Platform Enthusiast

![文章头图](https://miro.medium.com/v2/resize:fit:700/1*z56pdyjWXyhlmPh8EDNzRg.png)

作者：[The Platform Enthusiast](https://medium.com/@PlatformEnthusiast)

发布于 2026 年 2 月 16 日。

**在 Kubernetes 上落地可观测性，工具很多；要把链路、指标和日志串起来，OpenTelemetry（OTel）和 Grafana Loki 是两条常见主线。**

在 Kubernetes 里做可观测性，可选工具不少。现代分布式系统要真正看清应用行为、高效排障，得把链路（traces）、指标（metrics）和日志（logs）关联起来。其中，Otel 这类开源采集器几乎是标配。

OpenTelemetry（OTel）已是采集分布式链路与指标的行业标准框架；Grafana Loki 则是面向云原生、可水平扩展、成本友好的日志聚合系统。本文讲如何把 OTel 的遥测采集能力和 Loki 的存储与查询能力拼成一套统一的可观测性栈。

动手前请确认：Kubernetes 集群已就绪，且节点能从公网拉镜像。我们会安装 OTel 和 Grafana Loki。先从 OTel 开始——创建 `otel-server.yaml`：

```yaml
mode: daemonset

image:
  repository: otel/opentelemetry-collector-contrib
  # tag: 0.145.0  # 可选：指定版本，不填则用 chart 验证过的最新版

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

# OpenTelemetry Collector 配置
config:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

  processors:
    # 批处理，提升吞吐
    batch:
      timeout: 10s
      send_batch_size: 1024

    # 内存上限，防止 OOM
    memory_limiter:
      check_interval: 5s
      limit_mib: 400
      spike_limit_mib: 100

    # Kubernetes 资源探测
    resourcedetection:
      detectors: [env, system]
      timeout: 5s

    # 用 K8s 元数据丰富日志/指标
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

    # 为 Loki 生成易读标签
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

    # 附加元数据
    attributes:
      actions:
        - key: environment
          value: non-production
          action: insert

  exporters:
    # Prometheus 指标导出
    prometheus:
      endpoint: "0.0.0.0:8889"
      namespace: otel
      const_labels:
        environment: nonprod

    # Prometheus Remote Write（对接 Prometheus 服务端）
    prometheusremotewrite:
      endpoint: http://prometheus-server.monitoring.svc.cluster.local/api/v1/write
      tls:
        insecure: true

    # Loki 日志导出
    otlphttp/loki:
      endpoint: http://loki-gateway.monitoring.svc.cluster.local/otlp
      tls:
        insecure: true
      # 跨区/高延迟网络优化
      sending_queue:
        enabled: true
        queue_size: 5000
      retry_on_failure:
        enabled: true
        initial_interval: 5s
        max_elapsed_time: 300s

  service:
    pipelines:
      # 链路管道
      traces:
        receivers: [otlp]
        processors: [memory_limiter, resourcedetection, attributes, batch]
        exporters: [debug]

      # 指标管道
      metrics:
        receivers: [otlp, prometheus, hostmetrics]
        processors: [memory_limiter, resourcedetection, attributes, batch]
        exporters: [prometheus, prometheusremotewrite, debug]

      # 日志管道
      logs:
        receivers: [otlp, filelog]
        processors: [memory_limiter, k8sattributes, resource, resourcedetection, attributes, batch]
        exporters: [otlphttp/loki, debug]

# ClusterRole 段
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

# Service Account
serviceAccount:
  create: true
  name: otel-collector

# 安全上下文——读宿主机日志需要 root
podSecurityContext:
  runAsUser: 0
  runAsGroup: 0
  fsGroup: 0

# 挂载宿主机日志目录
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

# 非生产环境关闭自动扩缩
autoscaling:
  enabled: false
```

要点速览：

1. OTel 以 DaemonSet 形式部署在集群各节点。
2. Collector 配置分四块：**Receivers（输入）**、**Processors（清洗与丰富）**、**Exporters（输出）**、**Service / Pipelines（接线）**——下文逐块说明。
3. `clusterRole` 属于 Kubernetes RBAC（基于角色的访问控制），相当于一张「许可证」，告诉 API Server Collector 能看哪些资源、做哪些操作。
4. `autoscaling` 段用于管理 OTel Pod 的自动扩缩（本例关闭）。

OpenTelemetry Collector 是中心数据管道：夹在应用和监控后端（Prometheus、Loki）之间，负责采集、清洗、转发的脏活累活。

配置按数据流向分成四段：

## [1. Receivers（输入）](#1-receivers-the-inputs)

定义数据从哪来。本例里 Collector 监听：

1. **otlp**：应用通过 OpenTelemetry SDK 直推的数据。
2. **hostmetrics**：节点级 CPU、内存、磁盘等硬件指标。
3. **filelog**：尾随 `/var/log/pods/` 下的原始日志；可用正则从路径里抽出 namespace 和 pod 名，方便过滤。

## [2. Processors（清洗与丰富）](#2-processors-the-cleaning--enrichment)

数据出站前的加工环节：

1. **k8sattributes**：最关键的一个。它查 Kubernetes API，给日志/指标打上所属 Pod 的标签，例如 `pod_name`、`namespace`。
2. **resource**：把复杂元数据压成 Loki 友好的短标签，例如 `{pod="my-app"}`。
3. **batch**：攒够一批（如 8192 条或 200ms）再发，比逐行推送高效得多。
4. **memory_limiter**：保险丝——内存超限时丢数据，而不是把节点拖垮。

## [3. Exporters（输出）](#3-exporters-the-outputs)

定义数据去哪：

1. **prometheusremotewrite**：指标写入 Prometheus。
2. **otlphttp/loki**：日志推到 Loki；配了 `sending_queue` 以应对网络抖动。
3. **debug**：把数据打到 Collector 自己的控制台日志——查「为什么 Grafana 里看不到这条日志」时很好用。

## [4. Service / Pipelines（接线）](#4-service--pipelines-the-wiring)

把上面几块串起来，按数据类型定义路径：

- **指标管道**：Receivers（OTLP、hostmetrics）→ Processors → Exporters（Prometheus）。
- **日志管道**：Receivers（OTLP、filelog）→ Processors → Exporters（Loki）。

没有这套配置，日志和指标就是「盲的」——没标签、没压缩、很难查。它把原始文本和数字变成结构化、可检索的可观测性数据。

把上面的 YAML 保存好后，用 Helm 安装：

```bash
# 添加 OTel 仓库
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

# （可选）为监控栈单独建命名空间
kubectl create namespace monitoring

# 安装 OTel
helm install otel-collector open-telemetry/opentelemetry-collector \
  -f otel-server.yaml \
  --namespace monitoring
```

安装成功后确认 OTel Pod 在跑，接着装 Grafana 和 Prometheus。新建 `prometheus.yaml` 和 `grafana.yaml`：

```yaml
# prometheus.yaml
server:
  service:
    type: NodePort
    nodePort: 30090

  # 开启 Remote Write Receiver，供 OTel 写入
  extraFlags:
    - web.enable-remote-write-receiver
    - web.enable-lifecycle

  # 持久化存储
  persistentVolume:
    enabled: true
    size: 4Gi
    storageClass: ""  # 默认 StorageClass，按需修改

  # 数据保留
  retention: 15d

  # 全局设置
  global:
    scrape_interval: 15s
    evaluation_interval: 15s

# 节点指标（CPU、内存、磁盘）
nodeExporter:
  enabled: true

# 集群级指标（Deployment、Pod 状态等）
kubeStateMetrics:
  enabled: true
```

![prometheus.yaml 配置说明](https://miro.medium.com/v2/resize:fit:700/1*xNqE7lQWW07ZqNjZyuVV5w.png)

```yaml
# grafana.yaml
service:
  type: NodePort
  nodePort: 30085

# 持久化存储
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
  readOnlyRootFilesystem: false  # 未完全调优时 Grafana 部分操作需要

# 管理员账号
adminUser: admin
# 建议安装时用 --set 或 Secret 改掉默认密码
# adminPassword: strongpassword

# 自动配置 Prometheus 数据源
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

# Dashboard 提供方
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

# 预置 Dashboard：Node Exporter Full（1860）和 Kubernetes Pods（6417）
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

# 安全与微调
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
```

![grafana.yaml 配置说明](https://miro.medium.com/v2/resize:fit:700/1*FMUtsh0qf1miT5zwCVrKEg.png)

同样保存 YAML 后执行：

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana grafana/grafana \
  -f grafana.yaml \
  --namespace monitoring

helm install prometheus prometheus-community/prometheus \
  -f prometheus.yaml \
  --namespace monitoring
```

确认 Pod 正常后，浏览器访问 `http://<服务器 IP>:30085/login`。

![Grafana 登录页](https://miro.medium.com/v2/resize:fit:700/1*ZDXTLYsm3y3DzzLon5F0Wg.png)

用用户名 `admin`、密码 `strongpassword` 登录，然后继续装 Loki。创建 `loki.yaml`：

```yaml
# loki.yaml
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
    retention_period: 168h  # 保留 7 天
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
```

![loki.yaml 核心配置](https://miro.medium.com/v2/resize:fit:700/1*7UExZlqr-fe11nlQ7jwA5w.png)

![loki.yaml 数据保留设置](https://miro.medium.com/v2/resize:fit:700/1*jfaW36mk-yTajEIQY_0A0w.png)

![loki.yaml 服务与网关设置](https://miro.medium.com/v2/resize:fit:700/1*S6_HjLqKtryUcflTnd9oCg.png)

安装 Loki：

```bash
helm install loki grafana/loki -f loki.yaml -n monitoring
```

确认 Pod 运行正常。在 Grafana 里打开 **Explore**，数据源选 **Loki**。

![在 Grafana Explore 中选择 Loki](https://miro.medium.com/v2/resize:fit:700/1*xj6XnZvyAORP6HKDSxvAtA.png)

选好标签，点蓝色 **Refresh** 跑查询。到这里，Kubernetes 上的 Grafana Loki + OTel Pod 监控栈就搭好了。

![Grafana Loki 查询示例](https://miro.medium.com/v2/resize:fit:700/1*DK9MG0QVcQ8k3s7uGMfjmw.png)

![logger 服务日志样例](https://miro.medium.com/v2/resize:fit:700/1*mPn8pf_v3QwTxcnSOzWOLQ.png)
