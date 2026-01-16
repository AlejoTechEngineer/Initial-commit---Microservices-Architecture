# Arquitectura de Microservicios - Sistema de Gestión de Pedidos

## Autor
**Alejandro De Mendoza**  
Ingeniero Informático - Especialista en IA  
alejandro.mendoza.techengineer@gmail.com

---

## Descripción del Proyecto

Migración de una aplicación monolítica a arquitectura basada en microservicios para mejorar:
- Disponibilidad
- Escalabilidad  
- Facilidad de modificación
- Tolerancia a fallos

---

## Arquitectura

### Microservicios Implementados:

1. **API Gateway** (Puerto 5000)
   - Punto de entrada único
   - Enrutamiento a microservicios
   - Rate limiting y autenticación básica

2. **User Service** (Puerto 5001)
   - Gestión de usuarios
   - Autenticación
   - Base de datos: PostgreSQL

3. **Order Service** (Puerto 5002)
   - Gestión de pedidos
   - Estados de pedidos
   - Base de datos: MongoDB

4. **Payment Service** (Puerto 5003)
   - Procesamiento de pagos
   - Transacciones
   - Base de datos: PostgreSQL

### Comunicación:
- **Síncrona**: REST APIs (JSON)
- **Asíncrona**: RabbitMQ (eventos de negocio)

---

## Bases de Datos

| Servicio | Motor | Justificación |
|----------|-------|---------------|
| User Service | PostgreSQL | ACID, datos estructurados, integridad referencial |
| Order Service | MongoDB | Esquema flexible, alto volumen, escalabilidad horizontal |
| Payment Service | PostgreSQL | ACID crítico, consistencia fuerte, auditoría |

---

## Instalación y Ejecución

### Prerrequisitos:
```bash
- Docker Desktop instalado
- Docker Compose
- Git
- VS Code (opcional)
```

### Pasos:

1. **Clonar el repositorio:**
```bash
git clone <tu-repo-url>
cd microservices-ecommerce
```

2. **Levantar todos los servicios:**
```bash
docker-compose up --build
```

3. **Verificar que todo funciona:**
```bash
# Health check de cada servicio
curl http://localhost:5000/health  # API Gateway
curl http://localhost:5001/health  # User Service
curl http://localhost:5002/health  # Order Service
curl http://localhost:5003/health  # Payment Service
```

---

## Pruebas de APIs

### User Service:
```bash
# Obtener todos los usuarios
curl http://localhost:5000/api/users

# Status del servicio
curl http://localhost:5001/status
```

### Order Service:
```bash
# Obtener todos los pedidos
curl http://localhost:5000/api/orders

# Status del servicio
curl http://localhost:5002/status
```

### Payment Service:
```bash
# Obtener todos los pagos
curl http://localhost:5000/api/payments

# Status del servicio
curl http://localhost:5003/status
```

---

## Monitoreo

### Acceso a bases de datos:

**PostgreSQL (User & Payment Services):**
```bash
# Conectar a User Service DB
docker exec -it postgres-users psql -U postgres -d userdb

# Conectar a Payment Service DB
docker exec -it postgres-payments psql -U postgres -d paymentdb
```

**MongoDB (Order Service):**
```bash
# Conectar a MongoDB
docker exec -it mongodb mongosh

use orderdb
db.orders.find()
```

**RabbitMQ Management:**
```
URL: http://localhost:15672
User: guest
Pass: guest
```

---

## Detener Servicios

```bash
# Detener todos los contenedores
docker-compose down

# Detener y eliminar volúmenes (limpieza completa)
docker-compose down -v
```

---

## Estructura del Proyecto

```
microservices-ecommerce/
├── api-gateway/          # Gateway de entrada
├── user-service/         # Microservicio de usuarios
├── order-service/        # Microservicio de pedidos
├── payment-service/      # Microservicio de pagos
├── docs/                 # Documentación técnica
├── docker-compose.yml    # Orquestación de contenedores
└── README.md            # Este archivo
```

---

## Tecnologías Utilizadas

- **Backend**: Python 3.11 + Flask
- **Bases de Datos**: PostgreSQL 15, MongoDB 7
- **Mensajería**: RabbitMQ 3
- **Containerización**: Docker + Docker Compose
- **APIs**: RESTful JSON

---

## Documentación Adicional

- [Arquitectura Detallada](./docs/ARCHITECTURE.md)
- [Documentación de APIs](./docs/API_DOCUMENTATION.md)
- [Diagrama de Arquitectura](./architecture-diagram.md)

---

## Criterios Técnicos Aplicados

1. **Database per Service Pattern**: Cada microservicio gestiona su propia BD
2. **API Gateway Pattern**: Punto de entrada centralizado
3. **Event-Driven Architecture**: Comunicación asíncrona con RabbitMQ
4. **Health Checks**: Endpoints de monitoreo en cada servicio
5. **Containerización**: Despliegue consistente con Docker
6. **Separation of Concerns**: Cada servicio con responsabilidad única

---

## Notas

- Este proyecto es una implementación básica sin lógica de negocio completa
- Los endpoints /health y /status están implementados en todos los servicios
- Las bases de datos se crean automáticamente al levantar los contenedores
- RabbitMQ está configurado para desarrollo (guest/guest)

---

## Contacto

**Alejandro De Mendoza**  
📱 +57 311 2687118  
📧 alejandro.mendoza.techengineer@gmail.com  
📍 Bogotá, Colombia

---

## 📄 Licencia

Este proyecto fue desarrollado como prueba técnica para posición de Desarrollador Fullstack.
