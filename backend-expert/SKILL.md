---
name: backend-expert
description: Design and build production-grade backend systems including APIs, databases, authentication, queues, and caching. Use when the user asks to build APIs, create backend services, design database schemas, implement authentication, set up message queues, or architect server-side systems. Handles vague requests like "build a backend" or "create an API" by gathering requirements and creating implementation plans.
---

# Backend Development Expert

Build production-quality backend systems that are secure, scalable, and maintainable.

## Workflow

**CRITICAL: Step 0.5 (Planning) is MANDATORY for all backend work. You must invoke the planner skill before writing any code, even if requirements are specific and detailed.**

### 0. Handle Vague Requests (Discovery Mode)

When the user's request is broad or ambiguous (e.g., "build a backend", "create an API", "set up the server"), gather requirements before proceeding.

**Trigger phrases for discovery mode:**

- "build a backend"
- "create an API"
- "set up the server"
- "design the database"
- "implement authentication"
- "make it scalable"
- Any request lacking specific endpoints or data models

**Discovery questions - ask using AskUserQuestion:**

1. **What are you building?**
   - What is the application/service? (e.g., e-commerce, SaaS, real-time chat, data pipeline)
   - Who are the consumers? (web frontend, mobile app, third-party integrations, internal services)
   - What's the expected scale? (users, requests/second, data volume)

2. **What resources/entities do you need?**
   - List the main data models (users, products, orders, etc.)
   - What are the key relationships between them?
   - Any specific business rules or constraints?

3. **What operations are required?**
   - CRUD operations on which resources?
   - Complex queries or aggregations?
   - Real-time features (WebSockets, SSE)?
   - Background jobs or scheduled tasks?

4. **Technical constraints?**
   - Existing codebase or greenfield?
   - Required language/framework?
   - Database preferences (SQL vs NoSQL)?
   - Hosting environment (cloud provider, containers, serverless)?

**After discovery, create an implementation plan:**

```
Backend Implementation Plan:

Core Resources:
1. [Resource] - [Key fields and relationships]
2. [Resource] - [Key fields and relationships]
...

API Endpoints:
1. [Method] [Path] - [Purpose]
2. [Method] [Path] - [Purpose]
...

Suggested Build Order:
1. [ ] Database schema and migrations
2. [ ] Core data models and ORM setup
3. [ ] Authentication/authorization layer
4. [ ] [Most critical endpoints]
5. [ ] [Supporting endpoints in priority order]
6. [ ] Background jobs/queues (if needed)
7. [ ] Caching layer (if needed)
8. [ ] API documentation

Tech Stack:
- Runtime: [detected or chosen]
- Framework: [detected or chosen]
- Database: [detected or chosen]
- Auth: [strategy]

Architecture Notes:
- [Key architectural decisions]
- [Scalability considerations]
```

### 0.5 Create Implementation Plan (MANDATORY)

**IMPORTANT: This step is REQUIRED for ALL backend work.** Even when the user provides detailed specifications, comprehensive planning ensures architectural soundness, catches security blind spots, and validates the approach.

Before writing any code, spawn the **planner sub-agent** to create a comprehensive implementation plan.

**Use the Task tool with `subagent_type: planner`:**

```
Create a backend implementation plan.

Goal: [What we're building]

Context from user:
[User requirements from discovery or specific request]

Resources/Models:
[List of entities]

API Endpoints:
[List of endpoints]

Tech stack:
[Runtime, framework, database, auth approach]

Focus the plan on:
1. Identifying all constraints (security, scalability, data integrity)
2. Analyzing tradeoffs between approaches (database design, auth strategy, caching)
3. Defining clear implementation steps with verification criteria
4. Assessing risks (security vulnerabilities, performance bottlenecks, integration failures)

Return a structured plan with:
- Constraints (hard/soft/assumptions)
- Key tradeoffs and recommendations
- Ordered implementation steps with verification criteria
- Risk assessment
```

The planner sub-agent will explore the codebase, analyze constraints, and return a comprehensive plan. This keeps planning context isolated from the main conversation.

**After receiving the plan:**

1. Review it for completeness
2. For complex tradeoffs, spawn `council-chairman` sub-agent for multi-perspective review
3. Present the plan to the user for approval

**Do NOT skip this step.** Present the plan to the user for approval before building.

### 1. Detect Tech Stack

Before writing code, detect the project's existing technologies:

```
Detection checklist:
- [ ] Check package.json, requirements.txt, go.mod, Cargo.toml, pom.xml for runtime/framework
- [ ] Check for existing database config (prisma, sequelize, sqlalchemy, gorm, diesel)
- [ ] Check for auth patterns (JWT, sessions, OAuth providers)
- [ ] Check existing routes/controllers for conventions
- [ ] Check for existing middleware patterns
- [ ] Check environment files for service dependencies (Redis, RabbitMQ, etc.)
```

If no backend stack detected, ask the user:

- Which language/runtime they want
- Which framework (Express, FastAPI, Gin, Spring, etc.)
- Which database type (PostgreSQL, MongoDB, etc.)
- Authentication strategy (JWT, sessions, OAuth)

**You must match existing patterns.** If the codebase uses FastAPI with SQLAlchemy, generate FastAPI with SQLAlchemy.

### 2. Architecture Principles

Before generating code, establish clear architectural intentions:

**API Design:**

- RESTful resources with consistent naming (plural nouns: `/users`, `/orders`)
- Predictable URL structure (`/resources/:id/sub-resources`)
- Appropriate HTTP methods (GET reads, POST creates, PUT/PATCH updates, DELETE removes)
- Consistent response envelope (data, error, meta/pagination)
- API versioning strategy (URL path `/v1/` or header)

**Data Layer:**

- Normalize data appropriately (avoid over-normalization for read-heavy workloads)
- Index strategically (query patterns determine indexes)
- Use transactions for multi-step operations
- Implement soft deletes for audit trails when appropriate
- Plan for data migrations from day one

**Security:**

- Validate all input at the boundary (never trust client data)
- Use parameterized queries (prevent SQL injection)
- Implement proper authentication (secure token storage, rotation)
- Apply authorization at every endpoint (role-based or attribute-based)
- Rate limit sensitive endpoints (login, password reset)
- Sanitize output (prevent XSS in API responses)
- Use HTTPS everywhere, set security headers

**Error Handling:**

- Consistent error response format across all endpoints
- Appropriate HTTP status codes (don't return 200 for errors)
- Descriptive error messages for developers, safe messages for users
- Log errors with context (request ID, user ID, stack trace)
- Graceful degradation when dependencies fail

**Performance:**

- Cache aggressively at appropriate layers (HTTP cache, application cache, query cache)
- Use connection pooling for databases
- Paginate list endpoints (cursor-based for large datasets)
- Optimize N+1 queries (eager loading, dataloaders)
- Async operations for I/O-bound tasks

### 3. Generate Production Code

**Structure requirements:**

- Clear separation of concerns (routes, controllers, services, repositories)
- Dependency injection for testability
- Configuration management (environment variables, not hardcoded)
- Consistent file organization matching framework conventions

**Database requirements:**

- Migrations for all schema changes (never modify production directly)
- Seed data for development/testing
- Proper data types (UUIDs vs auto-increment, timestamps with timezone)
- Foreign key constraints where appropriate
- Indexes on frequently queried columns

**API requirements:**

- Input validation with clear error messages
- Request/response DTOs (don't expose internal models directly)
- Pagination for list endpoints
- Filtering and sorting where appropriate
- CORS configuration for web clients

**Authentication requirements:**

- Secure password hashing (bcrypt, argon2)
- Token expiration and refresh strategies
- Protect against timing attacks
- Invalidation mechanism for logout
- Multi-factor authentication hooks (if required)

### 4. Code Quality Standards

```
Quality checklist:
- [ ] All endpoints have input validation
- [ ] All database queries use parameterized inputs
- [ ] Error responses follow consistent format
- [ ] Sensitive data is not logged
- [ ] Environment variables for all configuration
- [ ] No hardcoded secrets or credentials
- [ ] Appropriate indexes on database tables
- [ ] Transactions wrap multi-step operations
- [ ] Rate limiting on authentication endpoints
```

## API Patterns

### Request Validation

Validate early, fail fast with helpful messages:

```
Validation approach:
- Required fields present
- Types are correct (string, number, email format)
- Values within allowed ranges
- Relationships exist (foreign keys valid)
- Business rules satisfied
```

### Response Format

Consistent envelope for all responses:

```json
// Success
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [{ "field": "email", "message": "Invalid format" }]
  }
}
```

### Authentication Flow

```
Standard JWT flow:
1. POST /auth/login - Returns access + refresh tokens
2. Access token in Authorization header for requests
3. POST /auth/refresh - Exchange refresh token for new access token
4. POST /auth/logout - Invalidate refresh token

Token storage:
- Access token: Short-lived (15-60 min), stateless validation
- Refresh token: Longer-lived (days/weeks), stored server-side for revocation
```

### Pagination

Cursor-based for large datasets, offset-based for small:

```
Cursor-based (recommended for scale):
GET /items?cursor=abc123&limit=20

Response includes:
- items: [...]
- nextCursor: "xyz789" (null if no more)
- hasMore: true/false

Offset-based (simpler, fine for small datasets):
GET /items?page=2&limit=20

Response includes:
- items: [...]
- total: 150
- page: 2
- totalPages: 8
```

## Database Patterns

### Schema Design

```
Best practices:
- Use UUIDs for public-facing IDs (avoid enumeration)
- Auto-increment integers for internal references (faster joins)
- created_at, updated_at on all tables
- deleted_at for soft deletes (when audit required)
- Appropriate nullable vs NOT NULL constraints
```

### Query Optimization

```
Index strategy:
- Primary keys (automatic)
- Foreign keys (for joins)
- Columns in WHERE clauses
- Columns in ORDER BY
- Composite indexes for multi-column queries (order matters)

Avoid:
- SELECT * (fetch only needed columns)
- N+1 queries (use joins or batching)
- Unindexed LIKE '%term%' (use full-text search)
- Large IN clauses (batch or use temp tables)
```

### Transactions

Wrap related operations to maintain consistency:

```
Transaction boundaries:
- Creating related records (user + profile)
- Transfer operations (debit + credit)
- Any multi-step operation that must succeed or fail together

Isolation levels:
- Read committed: Default, prevents dirty reads
- Repeatable read: For read-modify-write patterns
- Serializable: When absolute consistency required (rare, impacts performance)
```

## Background Processing

### Job Queues

For operations that don't need immediate response:

```
Queue candidates:
- Email sending
- Image/file processing
- Report generation
- External API calls
- Data aggregation

Implementation:
- Persistent queue (Redis, RabbitMQ, SQS)
- Retry logic with exponential backoff
- Dead letter queue for failed jobs
- Idempotency keys for safe retries
```

### Scheduled Tasks

```
Cron job patterns:
- Database cleanup (old sessions, expired tokens)
- Report generation
- Cache warming
- Health checks for external services
- Data synchronization
```

## Caching Strategy

```
Cache layers:
1. HTTP caching (Cache-Control headers for static resources)
2. CDN caching (for globally distributed content)
3. Application cache (Redis/Memcached for computed data)
4. Database query cache (for expensive queries)

Cache invalidation:
- Time-based expiration (TTL)
- Event-based invalidation (on write, clear related cache)
- Version keys (increment version to invalidate)

What to cache:
- Frequently read, rarely changed data
- Expensive computations
- External API responses
- Session data
```

## Output Format

When generating backend code:

1. Start with the data model/schema
2. Include migrations
3. Generate API routes with validation
4. Add authentication middleware
5. Include error handling
6. Note any assumptions about behavior
7. Provide brief architectural rationale for key decisions

If the request is ambiguous, ask clarifying questions about:

- Expected scale and performance requirements
- Security requirements (compliance, data sensitivity)
- Integration points (external services, webhooks)
- Deployment environment constraints
