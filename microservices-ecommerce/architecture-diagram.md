graph TB
    subgraph "Client Layer"
        Client[Cliente Web/Mobile]
    end

    subgraph "API Layer"
        Gateway[API Gateway<br/>:5000<br/>REST Routing]
    end

    subgraph "Microservices Layer"
        UserService[User Service<br/>:5001<br/>PostgreSQL]
        OrderService[Order Service<br/>:5002<br/>MongoDB]
        PaymentService[Payment Service<br/>:5003<br/>PostgreSQL]
    end

    subgraph "Data Layer"
        PostgresUsers[(PostgreSQL<br/>Users DB<br/>:5432)]
        MongoDB[(MongoDB<br/>Orders DB<br/>:27017)]
        PostgresPayments[(PostgreSQL<br/>Payments DB<br/>:5433)]
    end

    subgraph "Message Broker"
        RabbitMQ[RabbitMQ<br/>Event Bus<br/>:5672]
    end

    Client -->|HTTP/REST| Gateway
    Gateway -->|REST| UserService
    Gateway -->|REST| OrderService
    Gateway -->|REST| PaymentService

    UserService -->|SQL| PostgresUsers
    OrderService -->|NoSQL| MongoDB
    PaymentService -->|SQL| PostgresPayments

    UserService -.->|Events| RabbitMQ
    OrderService -.->|Events| RabbitMQ
    PaymentService -.->|Events| RabbitMQ

    RabbitMQ -.->|Subscribe| UserService
    RabbitMQ -.->|Subscribe| OrderService
    RabbitMQ -.->|Subscribe| PaymentService

    style Gateway fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style UserService fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style OrderService fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style PaymentService fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style PostgresUsers fill:#336791,stroke:#1A3A5C,stroke-width:2px,color:#fff
    style MongoDB fill:#47A248,stroke:#2E6B30,stroke-width:2px,color:#fff
    style PostgresPayments fill:#336791,stroke:#1A3A5C,stroke-width:2px,color:#fff
    style RabbitMQ fill:#FF6600,stroke:#CC5200,stroke-width:2px,color:#fff