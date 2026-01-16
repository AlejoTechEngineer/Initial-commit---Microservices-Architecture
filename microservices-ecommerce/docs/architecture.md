# 🏗️ Documentación de Arquitectura

## Autor
**Alejandro De Mendoza**  
Ingeniero Informático - Especialista en IA  
Fecha: 16/01/2026

---

## 1. Diseño de Arquitectura

### 1.1 Dominios de Negocio

La aplicación se divide en tres dominios principales siguiendo Domain-Driven Design (DDD):

#### **User Domain (Gestión de Usuarios)**
- **Responsabilidad**: Autenticación, autorización y gestión del ciclo de vida del usuario
- **Entidades**: User
- **Operaciones**: Registro, login, actualización de perfil, gestión de sesiones

#### **Order Domain (Gestión de Pedidos)**
- **Responsabilidad**: Creación, seguimiento y actualización de pedidos
- **Entidades**: Order, OrderItem
- **Operaciones**: Crear pedido, consultar estado, actualizar estado, cancelar

#### **Payment Domain (Gestión de Pagos)**
- **Responsabilidad**: Procesamiento de transacciones financieras
- **Entidades**: Payment, Transaction
- **Operaciones**: Procesar pago, consultar transacciones, reembolsos, auditoría

### 1.2 Módulos Independientes

Cada microservicio es completamente autónomo:

```
┌─────────────────────────────────────────────────────┐
│                   API Gateway                        │
│  • Enrutamiento                                      │
│  • Rate limiting                                     │
│  • Autenticación básica                             │
└──────────┬──────────────┬──────────────┬────────────┘
           │              │              │
    ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼───────┐
    │   User     │ │   Order    │ │  Payment   │
    │  Service   │ │  Service   │ │  Service   │
    │            │ │            │ │            │
    │ • Auth     │ │ • CRUD     │ │ • Process  │
    │ • Profile  │ │ • Status   │ │ • Validate │
    │ • Sessions │ │ • History  │ │ • Refund   │
    └──────┬─────┘ └─────┬──────┘ └────┬───────┘
           │              │              │
    ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼───────┐
    │ PostgreSQL │ │  MongoDB   │ │ PostgreSQL │
    └────────────┘ └────────────┘ └────────────┘
```

**Principios de independencia aplicados:**

1. **Database per Service**: Cada servicio tiene su propia base de datos
2. **No shared data**: Los servicios no acceden directamente a las BD de otros
3. **API-first communication**: Comunicación exclusivamente vía APIs REST
4. **Bounded Context**: Cada servicio gestiona su propio contexto de negocio

### 1.3 Selección de Motores de Base de Datos

| Microservicio | Motor | Justificación Técnica |
|---------------|-------|----------------------|
| **User Service** | **PostgreSQL 15** | • **ACID necesario**: Las operaciones de usuarios requieren transacciones atómicas<br>• **Datos estructurados**: Esquema relacional claro (users, roles, permissions)<br>• **Integridad referencial**: Foreign keys para relaciones<br>• **Consultas complejas**: JOINs para reportes y búsquedas avanzadas<br>• **Seguridad**: Control de acceso a nivel de fila (RLS)<br>• **Madurez**: Amplia documentación y estabilidad probada |
| **Order Service** | **MongoDB 7** | • **Esquema flexible**: Pedidos pueden tener estructuras variables (diferentes productos, atributos dinámicos)<br>• **Documentos embebidos**: Items del pedido se almacenan como subdocumentos<br>• **Alto volumen de escrituras**: Muchas actualizaciones de estado<br>• **Escalabilidad horizontal**: Sharding nativo para crecimiento<br>• **Historial**: Document versioning para auditoría<br>• **Performance**: Lecturas rápidas sin JOINs complejos |
| **Payment Service** | **PostgreSQL 15** | • **ACID crítico**: Transacciones financieras requieren consistencia absoluta<br>• **Atomicidad**: Operaciones de débito/crédito deben ser atómicas<br>• **Auditoría**: Logs de transacciones inmutables<br>• **Compliance**: Requisitos regulatorios (PCI-DSS)<br>• **Rollback**: Capacidad de revertir transacciones<br>• **Reporting**: Análisis financiero con SQL avanzado |

### 1.4 Patrones de Arquitectura Implementados

#### **API Gateway Pattern**
- Punto de entrada único para todas las peticiones
- Simplifica el consumo para clientes
- Implementa cross-cutting concerns (auth, rate limiting, logging)

#### **Database per Service Pattern**
- Cada microservicio gestiona su propia base de datos
- Evita acoplamiento por datos compartidos
- Permite evolución independiente de esquemas

#### **Event-Driven Architecture**
- Comunicación asíncrona vía RabbitMQ
- Desacoplamiento temporal entre servicios
- Garantía de entrega de eventos

---

## 2. Criterios Técnicos de Diseño

### 2.1 Disponibilidad

**Estrategias implementadas:**

1. **Health Checks**: Endpoints `/health` en cada servicio
2. **Retry Logic**: Reintentos automáticos en llamadas entre servicios
3. **Timeouts**: Configuración de timeouts para evitar cuelgues
4. **Circuit Breaker**: (Recomendado para producción usando Hystrix/Resilience4j)

### 2.2 Escalabilidad

**Mecanismos:**

1. **Escalado horizontal**: Contenedores Docker permiten múltiples instancias
2. **Load Balancing**: API Gateway puede distribuir carga
3. **Stateless services**: Servicios sin estado interno
4. **Database sharding**: MongoDB soporta particionamiento

**Capacidad de escalado por servicio:**

```
User Service:    1x → 5x (esperado: baja carga)
Order Service:   1x → 10x (esperado: alta carga)
Payment Service: 1x → 3x (esperado: media carga)
```

### 2.3 Facilidad de Modificación

**Principios aplicados:**

1. **Single Responsibility**: Cada servicio una responsabilidad
2. **Open/Closed Principle**: Extensible sin modificar código existente
3. **Dependency Inversion**: Servicios dependen de abstracciones
4. **API Versioning**: (Recomendado: `/api/v1/`, `/api/v2/`)

### 2.4 Tolerancia a Fallos

**Estrategias:**

1. **Graceful Degradation**: Si un servicio falla, los demás continúan
2. **Bulkhead Pattern**: Aislamiento de recursos por servicio
3. **Fallback Responses**: Respuestas por defecto en caso de error
4. **Async Communication**: RabbitMQ garantiza entrega de mensajes

---

## 3. Protocolos de Comunicación

### 3.1 Comparación de Protocolos

| Protocolo | Ventajas | Desventajas | Caso de Uso Ideal |
|-----------|----------|-------------|-------------------|
| **REST** | • Estándar HTTP<br>• Fácil debugging<br>• Cacheable<br>• Stateless | • Overhead JSON<br>• Acoplamiento temporal<br>• No ideal para streaming | • CRUD operations<br>• APIs públicas<br>• Integraciones web |
| **gRPC** | • Binario (Protobuf)<br>• Alta performance<br>• Streaming<br>• Tipado fuerte | • Complejidad<br>• Debug difícil<br>• No human-readable | • Comunicación interna<br>• Alta frecuencia<br>• Microservicios intensivos |
| **RabbitMQ** | • Desacoplamiento<br>• Garantía de entrega<br>• Pub/Sub<br>• Retry automático | • Latencia mayor<br>• Infraestructura extra<br>• Complejidad operativa | • Eventos de negocio<br>• Workflows asíncronos<br>• Notificaciones |
| **Kafka** | • Throughput alto<br>• Persistencia<br>• Event sourcing<br>• Replay | • Complejidad alta<br>• Overhead infraestructura<br>• Learning curve | • Streaming de datos<br>• Event log<br>• Analytics en tiempo real |

### 3.2 Decisión para Este Proyecto

**Arquitectura Híbrida: REST + RabbitMQ**

#### **REST para Comunicación Síncrona**

**Justificación:**
- Cliente necesita respuesta inmediata (UX)
- Operaciones CRUD estándar
- Fácil integración con frontends web/mobile
- Debugging simple con herramientas HTTP

**Casos de uso:**
```
GET  /api/users          → Obtener usuarios
POST /api/orders         → Crear pedido (respuesta inmediata)
GET  /api/payments/{id}  → Consultar estado de pago
```

#### **RabbitMQ para Comunicación Asíncrona**

**Justificación:**
- Desacoplamiento entre servicios
- Operaciones que no requieren respuesta inmediata
- Garantía de entrega (durabilidad de mensajes)
- Capacidad de retry automático

**Eventos del sistema:**
```
OrderCreated       → Payment Service procesa pago
PaymentCompleted   → Order Service actualiza estado a "paid"
PaymentFailed      → Order Service actualiza estado a "payment_failed"
OrderCancelled     → Payment Service ejecuta refund
UserUpdated        → Order/Payment Services actualizan cache
```

### 3.3 Flujo de Comunicación

#### Escenario: Crear un Pedido

```
┌────────┐         ┌─────────┐         ┌───────────┐
│ Client │         │ Gateway │         │   Order   │
└───┬────┘         └────┬────┘         │  Service  │
    │                   │              └─────┬─────┘
    │ POST /api/orders  │                    │
    ├──────────────────>│                    │
    │                   │ POST /orders       │
    │                   ├───────────────────>│
    │                   │                    │
    │                   │ {order_id: 123}    │
    │                   │<───────────────────┤
    │ {order_id: 123}   │                    │
    │<──────────────────┤                    │
    │                   │                    │
    │                   │                    │ Publish
    │                   │                    │ "OrderCreated"
    │                   │                    ├─────────┐
    │                   │                    │         │
    │                   │                    │   RabbitMQ
    │                   │                    │         │
    │                   │                    │<────────┘
    │                   │                    │
    │                   │              ┌─────▼─────┐
    │                   │              │  Payment  │
    │                   │              │  Service  │
    │                   │              └───────────┘
    │                   │              Subscribe to
    │                   │              "OrderCreated"
```

---

## 4. Consideraciones de Producción

### 4.1 Seguridad

- [ ] Implementar JWT para autenticación
- [ ] HTTPS/TLS para todas las comunicaciones
- [ ] Rate limiting en API Gateway
- [ ] Input validation en todos los endpoints
- [ ] Secrets management (AWS Secrets Manager / Vault)

### 4.2 Monitoreo

- [ ] Logging centralizado (ELK Stack)
- [ ] Métricas (Prometheus + Grafana)
- [ ] Tracing distribuido (Jaeger / Zipkin)
- [ ] Alertas (PagerDuty / Opsgenie)

### 4.3 CI/CD

- [ ] GitHub Actions para builds automáticos
- [ ] Tests unitarios (pytest)
- [ ] Tests de integración
- [ ] Deployment automático a staging
- [ ] Approval manual para producción

### 4.4 Infraestructura

**Recomendaciones para AWS:**

```
• API Gateway → AWS ALB (Application Load Balancer)
• Microservicios → AWS ECS Fargate / EKS
• PostgreSQL → AWS RDS (Multi-AZ)
• MongoDB → AWS DocumentDB / MongoDB Atlas
• RabbitMQ → Amazon MQ
• Cache → AWS ElastiCache (Redis)
```

---

## 5. Roadmap de Mejoras

### Fase 1 (MVP) - Actual ✅
- [x] Arquitectura de microservicios básica
- [x] APIs REST funcionales
- [x] Dockerización completa
- [x] Health checks

### Fase 2 (Mejoras)
- [ ] Implementar Circuit Breaker
- [ ] Agregar cache con Redis
- [ ] JWT authentication
- [ ] API versioning

### Fase 3 (Producción)
- [ ] Kubernetes deployment
- [ ] Service mesh (Istio)
- [ ] Observabilidad completa
- [ ] Auto-scaling policies

---

## Referencias

- [Microservices Patterns - Chris Richardson](https://microservices.io/patterns/)
- [Building Microservices - Sam Newman](https://samnewman.io/books/building_microservices_2nd_edition/)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Desarrollado por**: Alejandro De Mendoza  
**Email**: alejandro.mendoza.techengineer@gmail.com  
**Fecha**: 16/01/2026