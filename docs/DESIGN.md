# System Design Document

## Overview
This document describes the architecture and design decisions of the Akasa Air Analytics Dashboard.

## Architecture Patterns

### 1. Layered Architecture
- **Presentation Layer**: Streamlit UI
- **Business Logic Layer**: KPI engines, data processors
- **Data Access Layer**: Database manager, loaders
- **Data Layer**: MySQL database

### 2. Design Patterns Used
- **Singleton Pattern**: Database manager, KPI engines
- **Factory Pattern**: KPI creation
- **Strategy Pattern**: SQL vs Pandas processing
- **Template Method**: Base KPI class

## Database Design

### ER Diagram
```
customers (1) ─────< (N) orders
    │
    ├── customer_id (PK)
    ├── customer_name
    ├── mobile_number (UK)
    └── region
                                │
                                ├── order_id (PK)
                                ├── mobile_number (FK)
                                ├── order_date_time
                                ├── sku_id
                                ├── sku_count
                                └── total_amount
```

### Indexing Strategy
1. Primary keys on both tables
2. Foreign key index on orders.mobile_number
3. Index on order_date_time for time-based queries
4. Index on region for aggregation queries

## Data Flow

1. **Upload** → Raw files stored in `/data/raw`
2. **Validation** → Data validated and cleaned
3. **Loading** → Batch insert into MySQL
4. **Processing** → KPI calculation (SQL or Pandas)
5. **Visualization** → Plotly charts in Streamlit
6. **Export** → Download as CSV

## Security Measures

1. Parameterized queries (SQL injection prevention)
2. Environment variables for credentials
3. Connection pooling with timeouts
4. Input validation and sanitization
5. Error handling without exposing internals

## Performance Optimizations

1. **Caching**: Streamlit cache for expensive operations
2. **Connection Pooling**: Reuse database connections
3. **Batch Operations**: Bulk inserts for large datasets
4. **Lazy Loading**: Load data only when needed
5. **Indexing**: Strategic database indexes

## Scalability Considerations

1. **Horizontal Scaling**: Can add read replicas
2. **Vertical Scaling**: Increase MySQL resources
3. **Caching Layer**: Add Redis for session management
4. **Load Balancing**: Multiple Streamlit instances
5. **Data Partitioning**: Partition orders by date

## Technology Choices

| Component | Technology | Reason |
|-----------|-----------|--------|
| Backend | Python 3.8+ | Rich data science ecosystem |
| UI | Streamlit | Rapid development, interactive |
| Database | MySQL 8.0 | Reliable, ACID compliant |
| Charts | Plotly | Interactive, beautiful |
| Data Processing | Pandas | Powerful data manipulation |
| Containerization | Docker | Easy deployment |

## Future Enhancements

1. **Real-time Updates**: WebSocket for live data
2. **Machine Learning**: Predictive analytics
3. **Authentication**: User management system
4. **API Layer**: RESTful API endpoints
5. **Microservices**: Break into smaller services