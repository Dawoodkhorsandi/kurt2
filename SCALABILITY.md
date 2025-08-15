# Scaling Kurt: From Startup to Enterprise

This document outlines the strategies for scaling the Kurt URL shortening service to handle significant traffic growth. The application has been designed with a scalable, stateless architecture from the ground up, which makes horizontal scaling straightforward.

## Core Scaling Strategies

There are two primary ways to scale a web application:

*   **Vertical Scaling (Scaling Up)**: This involves increasing the resources of a single server—for example, upgrading to a more powerful CPU, adding more RAM, or using faster storage. While simple, this approach has physical limits and can become very expensive.

*   **Horizontal Scaling (Scaling Out)**: This involves adding more servers (or containers) to your resource pool and distributing the load between them. This is the preferred method for modern, high-traffic applications as it offers virtually limitless scalability and high availability. Kurt is designed for horizontal scaling.

---

## 1. Application Layer Scaling (`api_server` & `log_worker`)

Both the `api_server` and `log_worker` services are **stateless**. They do not store any session data locally and depend only on external services (PostgreSQL, Redis). This is the key to their scalability.

### Horizontal Scaling

You can scale these services horizontally by simply increasing the number of running containers. In `docker-compose.yml`, this is as simple as changing the `replicas` count:

```yaml
services:
  api_server:
    deploy:
      replicas: 5 # Scale from 2 to 5, or more
  log_worker:
    deploy:
      replicas: 3 # Scale as needed
```

### Fine-Tuning Gunicorn

The performance of the `api_server` is also dependent on its Gunicorn configuration.

*   **Workers**: The number of Gunicorn worker processes determines how many requests can be handled concurrently. A common formula is `(2 * number_of_cpu_cores) + 1`. You can set this with the `WEB_CONCURRENCY` environment variable.

*   **Worker Class**: Kurt uses `uvicorn.workers.UvicornWorker`, which is ideal for asyncio applications. For specific use cases, you might explore other worker types, but this is generally the best choice for FastAPI.

---

## 2. Load Balancing (NGINX and Beyond)

The `nginx` service acts as a reverse proxy and load balancer, distributing traffic across the `api_server` replicas.

### Scaling NGINX

For most use cases, a single NGINX instance is sufficient. You can vertically scale the server it runs on if needed. For extreme high availability, you can run multiple NGINX instances behind a DNS load balancer or a cloud provider's load balancer.

### Better Load Balancing

While NGINX's default round-robin load balancing is effective, more advanced strategies can improve performance:

*   **Least Connections**: Sends requests to the server with the fewest active connections. This is more efficient than round-robin if requests have varying completion times.
*   **Alternative Load Balancers**: For enterprise-grade performance and features, consider:
    *   **HAProxy**: A high-performance, open-source load balancer known for its efficiency and advanced features.
    *   **Cloud Load Balancers**: Services like AWS Elastic Load Balancer (ELB) or Google Cloud Load Balancing offer seamless scalability, health checks, and integration with other cloud services.

---

## 3. Database Scaling (PostgreSQL)

The database is often the most complex component to scale.

### Connection Pooling

Kurt already uses **Pgbouncer** for connection pooling. This is a critical first step, as it reduces the overhead of creating new database connections for each request.

### Read Replicas

A large portion of the application's workload involves reading data (retrieving the original URL). You can create one or more read-only replicas of your main database. You would then configure the application to direct all read queries to the replicas and write queries (like creating a new URL) to the primary database.

### Clustering & High Availability

To prevent the database from being a single point of failure, you can set up a PostgreSQL cluster. Using tools like **Patroni** or **Stolon**, you can create a high-availability cluster with automatic failover. If the primary database server fails, a replica is automatically promoted to be the new primary.

### Sharding

For applications with extremely high write volumes, a single primary database may not be enough. **Sharding** is the process of splitting your database into smaller, more manageable pieces (shards) and spreading them across multiple database servers. For example, you could shard the `urls` table based on the hash of the `short_code`. This is a complex undertaking and should only be considered when other scaling methods are insufficient.

---

## 4. Cache & Message Queue Scaling (Redis)

Redis is used for both caching and as a message queue.

### Redis Sentinel for High Availability

**Redis Sentinel** provides a high-availability solution for Redis. It monitors a set of Redis instances and can automatically perform a failover if the primary node becomes unavailable, promoting a replica to be the new primary.

### Redis Cluster for Sharding

If a single Redis node is not enough to handle your caching or messaging load, you can use **Redis Cluster**. Redis Cluster automatically shards your data across multiple Redis nodes. This provides both scalability (more nodes to handle more traffic) and high availability.
