---
title: "如何在 OpenTelemetry 中正确结构化日志"
title_en: "How to Structure Logs Properly in OpenTelemetry: A Complete Guide"
source_url: https://oneuptime.com/blog/post/2025-08-28-how-to-structure-logs-properly-in-opentelemetry/view
published_at: 2025-08-28
translated_at: 2026-09-02
tech_domain: backend
tags: [opentelemetry, logging, observability, nodejs, tracing]
cover_image: https://oneuptime.com/blog/post/2025-08-28-how-to-structure-logs-properly-in-opentelemetry/social-media.png
---

# 如何在 OpenTelemetry 中正确结构化日志

原文链接：<https://oneuptime.com/blog/post/2025-08-28-how-to-structure-logs-properly-in-opentelemetry/view>

![文章头图](https://oneuptime.com/blog/post/2025-08-28-how-to-structure-logs-properly-in-opentelemetry/social-media.png)

发布于 2025 年 8 月 28 日。

**日志（logs）是应用在运行过程中留下的详细「故事」。若在 OpenTelemetry 中做好结构化，它们将成为强大的排障工具，并能与追踪（traces）、指标（metrics）无缝衔接，让你获得完整的可观测性（observability）。**

在 OpenTelemetry 中高效记录日志，关键不只是「把事件记下来」，而是要用一种能讲清完整故事、能与其他遥测数据关联、并在出问题时提供可行动洞察的方式去记录。

## [为何在 OpenTelemetry 中结构化日志如此重要](#why-structure-matters-in-opentelemetry-logging)

传统日志往往产出彼此孤立的事件，在大规模场景下难以关联和分析。OpenTelemetry 结构化日志（structured logging）通过以下方式解决这一问题：

* **将日志与追踪和跨度（spans）关联**，获得完整请求上下文
* **标准化日志属性**，跨服务、跨团队保持一致
* **在可观测性平台上高效查询与过滤**
* **提供上下文增强**，加快排障速度
* **支持跨微服务的分布式追踪关联**

### [无结构日志的问题](#the-problem-with-unstructured-logs)

下面这些无结构日志语句展示了常见的反模式：把数据直接塞进消息字符串。当你需要分析成千上万条这样的日志时，不借助复杂的正则解析，就无法按用户过滤、按耗时区间查询，也无法按错误类型分组。

```
// ❌ Traditional unstructured logging - hard to query and analyze
console.log("User login failed for john@example.com with invalid password");
console.log("Database query took 150ms for user lookup");
console.log("Payment processing failed - card declined");
```

这类日志缺少上下文、关联和结构，在分布式系统中几乎无法有效分析。

### [OpenTelemetry 方案](#the-opentelemetry-solution)

结构化日志把日志消息与数据属性分开。每条信息都成为可查询字段，你可以按用户邮箱、耗时阈值、错误码或任意属性组合来过滤日志。

```
// ✅ Structured logging with OpenTelemetry
// Each attribute is a separate queryable field in your observability platform
logger.info("User authentication failed", {
  "user.email": "john@example.com",       // Queryable: find all logs for a specific user
  "auth.failure_reason": "invalid_password", // Filter by failure type
  "auth.attempt_count": 3,                // Alert when attempts exceed threshold
  "user.ip_address": "192.168.1.100"      // Track suspicious IPs
});

logger.debug("Database query executed", {
  "db.operation": "SELECT",               // Group by operation type
  "db.table": "users",                    // Filter by table
  "db.duration_ms": 150,                  // Create latency percentile charts
  "db.query_hash": "abc123"               // Identify slow query patterns
});

logger.error("Payment processing failed", {
  "payment.amount_usd": 99.99,            // Calculate failed payment volume
  "payment.method": "credit_card",        // Analyze failures by method
  "payment.failure_code": "card_declined", // Group by failure reason
  "order.id": "order-789"                 // Correlate with order details
});
```

## [在 Node.js 中配置 OpenTelemetry 日志](#setting-up-opentelemetry-logging-in-node-js)

### [安装](#installation)

安装 OpenTelemetry SDK、自动插桩包，以及用于日志记录的 Winston。`auto-instrumentations` 包会自动从常见 Node.js 库中采集遥测数据。

```
npm install @opentelemetry/api \
            @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-logs-otlp-http \
            @opentelemetry/instrumentation-winston \
            winston
```

### [OpenTelemetry 日志基础配置](#basic-opentelemetry-logging-setup)

以下配置初始化 OpenTelemetry，并将日志导出到 OTLP 端点。核心集成是 `WinstonInstrumentation`：它会自动把追踪 ID 和跨度 ID 注入每条 Winston 日志，从而实现日志与分布式追踪的关联。

```
// telemetry.ts - Initialize OpenTelemetry with logging support
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPLogExporter } from '@opentelemetry/exporter-logs-otlp-http';
import { BatchLogRecordProcessor } from '@opentelemetry/sdk-logs';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { WinstonInstrumentation } from '@opentelemetry/instrumentation-winston';

// Configure OTLP exporter to send logs to your observability backend
const logExporter = new OTLPLogExporter({
  url: 'https://oneuptime.com/otlp/v1/logs',  // OTLP HTTP endpoint
  headers: {
    'x-oneuptime-token': process.env.ONEUPTIME_OTLP_TOKEN,  // Auth token
  },
});

// Batch processor improves performance by grouping logs before sending
const logProcessor = new BatchLogRecordProcessor(logExporter, {
  exportTimeoutMillis: 5000,      // Max time to wait for export
  maxExportBatchSize: 100,        // Max logs per batch
  scheduledDelayMillis: 2000,     // Time between batch exports
});

// Initialize the OpenTelemetry SDK with service metadata and instrumentations
const sdk = new NodeSDK({
  // Resource attributes identify your service in the observability platform
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'my-node-app',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.SERVICE_INSTANCE_ID]: process.env.HOSTNAME || 'localhost',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
  instrumentations: [
    // Auto-instrument common Node.js libraries (http, express, pg, etc.)
    getNodeAutoInstrumentations(),
    // Winston instrumentation automatically adds trace context to logs
    new WinstonInstrumentation({
      // logHook runs for each log entry within an active span
      logHook: (span, record) => {
        if (span && span.spanContext().traceId) {
          // Inject trace IDs for log-to-trace correlation
          record['trace_id'] = span.spanContext().traceId;
          record['span_id'] = span.spanContext().spanId;
        }
      },
    }),
  ],
  logRecordProcessor: logProcessor,
});

// Start telemetry collection - call this before your app starts
sdk.start();

console.log('OpenTelemetry logging initialized with OneUptime OTLP exporter');
```

### [Winston 日志器配置](#winston-logger-configuration)

这份 Winston 配置会创建一个可用于生产的日志器，并自动注入 OpenTelemetry 追踪上下文。自定义的 `correlationFormat` 会从当前活跃跨度中提取追踪 ID 和跨度 ID，让你在可观测性界面中可以从日志条目直接跳转到对应的分布式追踪。

```
// logger.ts - Winston logger with OpenTelemetry trace correlation
import winston from 'winston';
import { trace, context } from '@opentelemetry/api';

// Custom Winston format that injects OpenTelemetry trace context
const correlationFormat = winston.format((info) => {
  // Look up the currently active span from OpenTelemetry context
  const activeSpan = trace.getActiveSpan();
  if (activeSpan) {
    const spanContext = activeSpan.spanContext();
    // These IDs enable log-to-trace correlation in your observability UI
    info.trace_id = spanContext.traceId;   // Links to distributed trace
    info.span_id = spanContext.spanId;     // Links to specific operation
    info.trace_flags = spanContext.traceFlags;  // Sampling decision
  }

  // Include service metadata for filtering in multi-service environments
  info.service = {
    name: process.env.SERVICE_NAME || 'my-node-app',
    version: process.env.SERVICE_VERSION || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
  };

  return info;
});

// Create Winston logger with combined formatting and multiple transports
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',  // Configurable via environment
  format: winston.format.combine(
    // ISO 8601 timestamp for consistent time parsing
    winston.format.timestamp({
      format: 'YYYY-MM-DDTHH:mm:ss.SSSZ'
    }),
    correlationFormat(),                    // Inject trace context
    winston.format.errors({ stack: true }), // Include stack traces for errors
    winston.format.json()                   // Output as JSON for parsing
  ),
  defaultMeta: {
    component: 'application'  // Default field added to all logs
  },
  transports: [
    // Console transport with colors for local development
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    // File transport with rotation for production
    new winston.transports.File({
      filename: 'logs/app.log',
      maxsize: 10000000,  // Rotate at 10MB
      maxFiles: 5,        // Keep 5 rotated files
    }),
  ],
});

export { logger };
```

## [结构化日志的核心原则](#core-principles-of-structured-logging)

### [1. 追踪与跨度关联](#1-trace-and-span-correlation)

OpenTelemetry 日志最强大的能力，是与追踪和跨度自动关联。下面的 `StructuredLogger` 类提供的方法会自动从当前执行上下文中提取追踪信息并附加到日志条目，让你在日志与追踪之间无缝跳转。

```
// structured-logger.ts - Logger wrapper with automatic trace correlation
import { logger } from './logger';
import { trace, SpanStatusCode } from '@opentelemetry/api';

export class StructuredLogger {
  /**
   * Log a message with automatic trace context from the active span.
   * Use this for all logging within traced operations.
   */
  static logInSpan(level: string, message: string, attributes: Record<string, any> = {}) {
    const activeSpan = trace.getActiveSpan();

    if (activeSpan) {
      // Extract trace context for correlation in observability UI
      const spanContext = activeSpan.spanContext();
      attributes.trace_id = spanContext.traceId;  // Links to distributed trace
      attributes.span_id = spanContext.spanId;    // Links to specific span
    }

    // Delegate to Winston logger with enriched attributes
    logger[level](message, attributes);
  }

  /**
   * Log with explicit trace correlation IDs.
   * Use when logging outside of an active span context (e.g., from queued jobs).
   */
  static logWithCorrelation(
    level: string,
    message: string,
    traceId: string,
    spanId: string,
    attributes: Record<string, any> = {}
  ) {
    logger[level](message, {
      ...attributes,
      trace_id: traceId,
      span_id: spanId,
    });
  }

  /**
   * Log business domain events with consistent structure.
   * Use for important business milestones: user signups, orders, payments, etc.
   */
  static logBusinessEvent(
    event: string,
    entityType: string,
    entityId: string,
    attributes: Record<string, any> = {}
  ) {
    this.logInSpan('info', `Business event: ${event}`, {
      event_type: 'business',     // Differentiates from technical logs
      event_name: event,          // e.g., 'user_created', 'order_placed'
      entity_type: entityType,    // e.g., 'user', 'order', 'payment'
      entity_id: entityId,        // Primary key of the entity
      ...attributes,
    });
  }
}
```

### [2. 语义属性与约定](#2-semantic-attributes-and-conventions)

OpenTelemetry 为常见遥测属性定义了语义约定（semantic conventions）。使用这些标准名称可以保证跨服务、跨语言、跨团队的一致性。下面的 `SemanticLogger` 类用规范命名的属性封装了常见操作。

```
// semantic-logging.ts - Logging helpers using OpenTelemetry semantic conventions
import { StructuredLogger } from './structured-logger';
import { SemanticAttributes } from '@opentelemetry/semantic-conventions';

export class SemanticLogger {
  /**
   * Log HTTP request completion with standard semantic attributes.
   * Captures method, URL, status, timing, and size for request analysis.
   */
  static logHttpRequest(req: any, res: any, duration: number, error?: Error) {
    const attributes = {
      // Standard OTel semantic attributes for HTTP
      [SemanticAttributes.HTTP_METHOD]: req.method,       // GET, POST, etc.
      [SemanticAttributes.HTTP_URL]: req.url,             // Full request URL
      [SemanticAttributes.HTTP_STATUS_CODE]: res.statusCode,  // 200, 404, 500, etc.
      [SemanticAttributes.HTTP_RESPONSE_CONTENT_LENGTH]: res.get('content-length') || 0,
      [SemanticAttributes.HTTP_REQUEST_CONTENT_LENGTH]: req.get('content-length') || 0,
      [SemanticAttributes.HTTP_USER_AGENT]: req.get('user-agent'),
      // Custom attributes for latency analysis
      'http.duration_ms': duration,                       // Request processing time
      'http.route': req.route?.path,                      // Route pattern for grouping
    };

    if (error) {
      attributes.error = true;
      attributes.error_message = error.message;
      attributes.error_stack = error.stack;
      StructuredLogger.logInSpan('error', 'HTTP request failed', attributes);
    } else {
      StructuredLogger.logInSpan('info', 'HTTP request completed', attributes);
    }
  }

  /**
   * Log database operations with semantic attributes.
   * Enables query performance analysis and error tracking by table/operation.
   */
  static logDatabaseOperation(
    operation: string,
    table: string,
    duration: number,
    rowsAffected?: number,
    error?: Error
  ) {
    const attributes = {
      // Standard OTel semantic attributes for databases
      [SemanticAttributes.DB_OPERATION]: operation,  // SELECT, INSERT, UPDATE, DELETE
      [SemanticAttributes.DB_SQL_TABLE]: table,      // Table name for filtering
      'db.duration_ms': duration,                    // Query execution time
      'db.rows_affected': rowsAffected || 0,         // For mutation tracking
    };

    if (error) {
      attributes.error = true;
      attributes.error_message = error.message;
      StructuredLogger.logInSpan('error', 'Database operation failed', attributes);
    } else {
      // Use debug level for routine DB operations to reduce noise
      StructuredLogger.logInSpan('debug', 'Database operation completed', attributes);
    }
  }

  /**
   * Log user actions for audit trails and behavior analysis.
   * Use for significant user interactions like logins, settings changes, etc.
   */
  static logUserAction(
    userId: string,
    action: string,
    resource: string,
    metadata: Record<string, any> = {}
  ) {
    StructuredLogger.logInSpan('info', 'User action performed', {
      'user.id': userId,           // Who performed the action
      'user.action': action,       // What they did (e.g., 'login', 'update_profile')
      'user.resource': resource,   // What they acted on
      event_type: 'user_action',   // Categorize for filtering
      ...metadata,
    });
  }
}
```

### [3. Express.js 中间件集成](#3-express-js-middleware-integration)

该中间件会自动记录每条 HTTP 请求，包含耗时、追踪关联，以及返回给客户端的请求 ID。它包装了 `res.end`，在路由处理完成后捕获响应，从而准确测量耗时。

```
// middleware/logging-middleware.ts - Automatic request logging for Express
import { Request, Response, NextFunction } from 'express';
import { SemanticLogger } from '../semantic-logging';
import { trace, context } from '@opentelemetry/api';

interface LoggedRequest extends Request {
  startTime?: number;
  correlationId?: string;
}

export function loggingMiddleware(req: LoggedRequest, res: Response, next: NextFunction) {
  req.startTime = Date.now();
  req.correlationId = generateCorrelationId();

  // Create a span for the request
  const tracer = trace.getTracer('http-middleware');
  const span = tracer.startSpan(`${req.method} ${req.path}`);

  // Set request attributes on the span
  span.setAttributes({
    'http.method': req.method,
    'http.url': req.url,
    'http.user_agent': req.get('user-agent') || '',
    'correlation.id': req.correlationId,
  });

  // Log request start
  context.with(trace.setSpan(context.active(), span), () => {
    SemanticLogger.logHttpRequest(req, { statusCode: 0 }, 0);
  });

  // Override res.end to capture response
  const originalEnd = res.end;
  res.end = function(chunk: any, encoding?: any) {
    const duration = Date.now() - (req.startTime || Date.now());
    
    // Log request completion within span context
    context.with(trace.setSpan(context.active(), span), () => {
      SemanticLogger.logHttpRequest(req, res, duration);
    });

    span.end();
    originalEnd.call(this, chunk, encoding);
  };

  next();
}

function generateCorrelationId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
```

## [高级日志模式](#advanced-logging-patterns)

### [1. 上下文日志增强](#1-contextual-log-enrichment)

`AsyncLocalStorage` 让你无需在每个函数调用中显式传递参数，就能维护请求级上下文。下面的增强器会自动把用户 ID、租户 ID 和关联 ID 添加到请求执行流程内的所有日志中。

```
// context-enricher.ts - Request-scoped logging context using AsyncLocalStorage
import { AsyncLocalStorage } from 'async_hooks';
import { logger } from './logger';

interface RequestContext {
  correlationId: string;
  userId?: string;
  tenantId?: string;
  sessionId?: string;
  requestId?: string;
}

export class ContextEnricher {
  private static storage = new AsyncLocalStorage<RequestContext>();

  // Set context for the current async execution
  static setContext(context: RequestContext, fn: () => void) {
    this.storage.run(context, fn);
  }

  // Get current context
  static getContext(): RequestContext | undefined {
    return this.storage.getStore();
  }

  // Enhanced logger that automatically includes context
  static createContextLogger() {
    return {
      info: (message: string, attributes: Record<string, any> = {}) => {
        const context = this.getContext();
        logger.info(message, { ...attributes, ...context });
      },
      warn: (message: string, attributes: Record<string, any> = {}) => {
        const context = this.getContext();
        logger.warn(message, { ...attributes, ...context });
      },
      error: (message: string, attributes: Record<string, any> = {}) => {
        const context = this.getContext();
        logger.error(message, { ...attributes, ...context });
      },
      debug: (message: string, attributes: Record<string, any> = {}) => {
        const context = this.getContext();
        logger.debug(message, { ...attributes, ...context });
      },
    };
  }
}

// Usage in Express middleware
export function contextMiddleware(req: any, res: Response, next: NextFunction) {
  const context: RequestContext = {
    correlationId: req.correlationId || generateCorrelationId(),
    userId: req.user?.id,
    tenantId: req.tenant?.id,
    sessionId: req.session?.id,
    requestId: req.id,
  };

  ContextEnricher.setContext(context, () => {
    next();
  });
}
```

### [2. 带堆栈跟踪的错误日志](#2-error-logging-with-stack-traces)

这个错误日志器不仅会在日志中记录错误详情，还会把当前 OpenTelemetry 跨度标记为错误，确保错误同时出现在日志检索和追踪分析视图中，且上下文保持同步。

```
// error-logging.ts - Unified error logging for logs and traces
import { StructuredLogger } from './structured-logger';
import { trace, SpanStatusCode } from '@opentelemetry/api';

export class ErrorLogger {
  static logError(error: Error, context: Record<string, any> = {}) {
    const activeSpan = trace.getActiveSpan();
    
    // Mark span as error if available
    if (activeSpan) {
      activeSpan.recordException(error);
      activeSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message,
      });
    }

    StructuredLogger.logInSpan('error', error.message, {
      error_type: error.constructor.name,
      error_message: error.message,
      error_stack: error.stack,
      error_code: (error as any).code,
      ...context,
    });
  }

  static logBusinessError(
    errorCode: string,
    errorMessage: string,
    entityType: string,
    entityId: string,
    metadata: Record<string, any> = {}
  ) {
    StructuredLogger.logInSpan('error', errorMessage, {
      error_type: 'business_error',
      error_code: errorCode,
      error_message: errorMessage,
      entity_type: entityType,
      entity_id: entityId,
      ...metadata,
    });
  }

  static async logAsyncError<T>(
    operation: string,
    fn: () => Promise<T>,
    context: Record<string, any> = {}
  ): Promise<T> {
    try {
      StructuredLogger.logInSpan('debug', `Starting operation: ${operation}`, context);
      const result = await fn();
      StructuredLogger.logInSpan('debug', `Completed operation: ${operation}`, context);
      return result;
    } catch (error) {
      this.logError(error as Error, {
        operation,
        ...context,
      });
      throw error;
    }
  }
}
```

### [3. 性能日志](#3-performance-logging)

这些性能辅助函数用 `process.hrtime.bigint()` 对操作进行高精度计时。无论成功还是失败，都会自动记录操作耗时，便于发现慢操作并构建性能看板。

```
// performance-logging.ts - Timing helpers for operation performance tracking
import { StructuredLogger } from './structured-logger';

export class PerformanceLogger {
  static timeOperation<T>(
    operationName: string,
    fn: () => T,
    context: Record<string, any> = {}
  ): T {
    const startTime = process.hrtime.bigint();
    
    try {
      const result = fn();
      const duration = Number(process.hrtime.bigint() - startTime) / 1e6; // Convert to ms
      
      StructuredLogger.logInSpan('debug', `Operation completed: ${operationName}`, {
        operation_name: operationName,
        duration_ms: duration,
        status: 'success',
        ...context,
      });
      
      return result;
    } catch (error) {
      const duration = Number(process.hrtime.bigint() - startTime) / 1e6;
      
      StructuredLogger.logInSpan('error', `Operation failed: ${operationName}`, {
        operation_name: operationName,
        duration_ms: duration,
        status: 'error',
        error_message: (error as Error).message,
        ...context,
      });
      
      throw error;
    }
  }

  static async timeAsyncOperation<T>(
    operationName: string,
    fn: () => Promise<T>,
    context: Record<string, any> = {}
  ): Promise<T> {
    const startTime = process.hrtime.bigint();
    
    try {
      const result = await fn();
      const duration = Number(process.hrtime.bigint() - startTime) / 1e6;
      
      StructuredLogger.logInSpan('debug', `Async operation completed: ${operationName}`, {
        operation_name: operationName,
        duration_ms: duration,
        status: 'success',
        ...context,
      });
      
      return result;
    } catch (error) {
      const duration = Number(process.hrtime.bigint() - startTime) / 1e6;
      
      StructuredLogger.logInSpan('error', `Async operation failed: ${operationName}`, {
        operation_name: operationName,
        duration_ms: duration,
        status: 'error',
        error_message: (error as Error).message,
        ...context,
      });
      
      throw error;
    }
  }
}
```

## [真实场景实现示例](#real-world-implementation-examples)

### [1. 带完整日志的用户服务](#1-user-service-with-comprehensive-logging)

这个真实服务示例展示了如何把上述日志工具组合成一套连贯的实现。注意业务事件、数据库操作和错误都采用了统一的结构，并自动与追踪关联。

```
// services/user-service.ts - Example service with comprehensive structured logging
import { SemanticLogger } from '../semantic-logging';
import { ErrorLogger } from '../error-logging';
import { PerformanceLogger } from '../performance-logging';
import { StructuredLogger } from '../structured-logger';

export class UserService {
  async createUser(userData: any): Promise<any> {
    return PerformanceLogger.timeAsyncOperation(
      'user_creation',
      async () => {
        StructuredLogger.logBusinessEvent(
          'user_creation_started',
          'user',
          userData.email,
          {
            user_data: {
              email: userData.email,
              role: userData.role,
              source: userData.source,
            }
          }
        );

        try {
          // Validate user data
          this.validateUserData(userData);

          // Check if user exists
          const existingUser = await this.findUserByEmail(userData.email);
          if (existingUser) {
            ErrorLogger.logBusinessError(
              'USER_ALREADY_EXISTS',
              'User with this email already exists',
              'user',
              userData.email,
              { attempted_email: userData.email }
            );
            throw new Error('User already exists');
          }

          // Create user in database
          const user = await this.saveUserToDatabase(userData);

          // Log successful creation
          StructuredLogger.logBusinessEvent(
            'user_created',
            'user',
            user.id,
            {
              user_id: user.id,
              user_email: user.email,
              user_role: user.role,
              created_at: user.createdAt,
            }
          );

          // Send welcome email
          await this.sendWelcomeEmail(user);

          return user;
        } catch (error) {
          ErrorLogger.logError(error as Error, {
            operation: 'user_creation',
            user_email: userData.email,
          });
          throw error;
        }
      },
      { operation_type: 'user_management' }
    );
  }

  private async findUserByEmail(email: string): Promise<any> {
    return PerformanceLogger.timeAsyncOperation(
      'database_user_lookup',
      async () => {
        SemanticLogger.logDatabaseOperation(
          'SELECT',
          'users',
          0, // Duration will be set by the performance logger
          0
        );
        
        // Simulate database call
        return null; // User not found
      },
      {
        query_type: 'user_lookup',
        lookup_field: 'email',
      }
    );
  }

  private validateUserData(userData: any): void {
    StructuredLogger.logInSpan('debug', 'Validating user data', {
      validation_fields: Object.keys(userData),
    });

    if (!userData.email || !userData.email.includes('@')) {
      ErrorLogger.logBusinessError(
        'INVALID_EMAIL',
        'Invalid email format provided',
        'user',
        userData.email || 'unknown'
      );
      throw new Error('Invalid email format');
    }

    // More validation...
  }

  private async saveUserToDatabase(userData: any): Promise<any> {
    return PerformanceLogger.timeAsyncOperation(
      'database_user_insert',
      async () => {
        // Simulate database save
        const user = {
          id: `user_${Date.now()}`,
          ...userData,
          createdAt: new Date().toISOString(),
        };

        SemanticLogger.logDatabaseOperation(
          'INSERT',
          'users',
          50, // Simulated duration
          1 // One row affected
        );

        return user;
      },
      { operation_type: 'persistence' }
    );
  }

  private async sendWelcomeEmail(user: any): Promise<void> {
    try {
      StructuredLogger.logInSpan('info', 'Sending welcome email', {
        user_id: user.id,
        user_email: user.email,
        email_type: 'welcome',
      });

      // Simulate email sending
      await new Promise(resolve => setTimeout(resolve, 100));

      StructuredLogger.logInSpan('info', 'Welcome email sent successfully', {
        user_id: user.id,
        user_email: user.email,
        email_type: 'welcome',
        status: 'sent',
      });
    } catch (error) {
      ErrorLogger.logError(error as Error, {
        operation: 'welcome_email',
        user_id: user.id,
        user_email: user.email,
      });
      // Don't throw - welcome email failure shouldn't fail user creation
    }
  }
}
```

### [2. 带完整日志的 API 路由](#2-api-route-with-full-logging)

这个 Express 路由处理函数展示了完整模式：为请求创建跨度、在首尾记录日志、设置跨度属性供追踪分析，并确保错误被正确捕获和记录。

```
// routes/users.ts - API endpoint with full observability integration
import { Router, Request, Response } from 'express';
import { UserService } from '../services/user-service';
import { ContextEnricher } from '../context-enricher';
import { trace } from '@opentelemetry/api';

const router = Router();
const userService = new UserService();
const contextLogger = ContextEnricher.createContextLogger();

router.post('/users', async (req: Request, res: Response) => {
  const tracer = trace.getTracer('user-api');
  const span = tracer.startSpan('POST /users');

  try {
    span.setAttributes({
      'http.method': 'POST',
      'http.route': '/users',
      'request.body_size': JSON.stringify(req.body).length,
    });

    contextLogger.info('User creation request received', {
      request_id: req.id,
      body_keys: Object.keys(req.body),
    });

    // Validate request
    if (!req.body.email) {
      contextLogger.warn('Invalid request - missing email', {
        request_body: req.body,
      });
      
      span.setAttributes({
        'error': true,
        'error.type': 'validation_error',
      });
      
      return res.status(400).json({
        error: 'Email is required',
        code: 'MISSING_EMAIL'
      });
    }

    // Create user
    const user = await userService.createUser(req.body);

    contextLogger.info('User created successfully', {
      user_id: user.id,
      user_email: user.email,
    });

    span.setAttributes({
      'user.id': user.id,
      'user.email': user.email,
      'response.status_code': 201,
    });

    res.status(201).json({
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        createdAt: user.createdAt,
      }
    });

  } catch (error) {
    contextLogger.error('User creation failed', {
      error_message: (error as Error).message,
      request_body: req.body,
    });

    span.setAttributes({
      'error': true,
      'error.message': (error as Error).message,
      'response.status_code': 500,
    });

    res.status(500).json({
      error: 'Internal server error',
      message: (error as Error).message
    });
  } finally {
    span.end();
  }
});

export { router as userRoutes };
```

## [最佳实践与反模式](#best-practices-and-anti-patterns)

### [✅ 最佳实践](#best-practices)

1. **始终与追踪关联**

```
// Always log within span context for correlation
StructuredLogger.logInSpan('info', 'Operation completed', attributes);
```

2. **使用语义属性**

```
// Follow OpenTelemetry semantic conventions
{
  [SemanticAttributes.HTTP_METHOD]: 'POST',
  [SemanticAttributes.HTTP_STATUS_CODE]: 200,
  [SemanticAttributes.ENDUSER_ID]: userId,
}
```

3. **合理设置日志级别**

```
// ERROR: System errors, exceptions, failures
// WARN: Recoverable errors, deprecated usage, unusual conditions
// INFO: Important business events, request/response logging
// DEBUG: Detailed execution flow, debugging information
```

4. **包含上下文信息**

```
// Rich context helps with debugging
logger.info('Payment processed', {
  payment_id: 'pay_123',
  amount_usd: 99.99,
  user_id: 'user_456',
  merchant_id: 'merchant_789',
  payment_method: 'credit_card',
  currency: 'USD',
  processing_time_ms: 1500,
});
```

### [❌ 反模式](#anti-patterns)

1. **记录敏感信息**

```
// DON'T: Log sensitive data
logger.info('User login', {
  password: user.password, // ❌ Never log passwords
  credit_card: user.card,  // ❌ Never log PII
});

// DO: Log safely
logger.info('User login', {
  user_id: user.id,
  login_method: 'password',
  has_mfa: user.mfaEnabled,
});
```

2. **高基数属性**

```
// DON'T: Use unbounded values as attributes
logger.info('Request processed', {
  timestamp: new Date().toISOString(), // ❌ High cardinality
  unique_id: generateUniqueId(),       // ❌ Unbounded values
});

// DO: Use bounded, meaningful attributes
logger.info('Request processed', {
  request_type: 'api',
  endpoint_category: 'user_management',
  status: 'success',
});
```

3. **在循环中无节制地打日志**

```
// DON'T: Log every iteration
items.forEach(item => {
  logger.debug('Processing item', { item_id: item.id }); // ❌ Too many logs
});

// DO: Log summaries or sample
logger.info('Processing items batch', { 
  batch_size: items.length,
  batch_id: batchId 
});
```

## [总结](#final-thoughts)

在 OpenTelemetry 中正确结构化日志，能把日志从简单的文本记录变成强大的可观测性数据，并与追踪、指标无缝关联。核心原则如下：

1. **关联至上**：始终把日志与追踪、跨度链接起来
2. **一切结构化**：使用一致的属性命名和语义约定
3. **上下文很重要**：包含相关的业务和技术上下文
4. **智能采样**：并非每条日志都需要全量采集
5. **测试你的日志**：确保日志结构按预期工作

请记住：

* **日志告诉你系统里发生了什么以及为什么**
* **结构化日志支持强大的查询与分析**
* **与追踪关联能大幅加快排障速度**
* **一致的属性命名提升跨服务的可检索性**

从基础的关联和语义属性入手，随着可观测性需求增长，再逐步加入上下文增强、智能采样等更高级的模式。

> 优秀的日志记录不在于「什么都记」，而在于「用对的方式记下该记的东西」——这样出问题时，你才有足够的上下文快速定位并解决。

准备好用 OpenTelemetry 落地结构化日志了吗？[OneUptime](https://oneuptime.com/) 提供完整的日志管理能力，原生支持 OpenTelemetry，自动与追踪和指标关联，并提供强大的查询能力，帮助你更快排障、更深入理解系统。
