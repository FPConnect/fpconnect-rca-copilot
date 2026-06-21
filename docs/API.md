# API Reference

Base URL: `http://localhost:8000`

## Authentication

### Register
```
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123!",
  "full_name": "John Doe",
  "role": "user"
}

Response 201:
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user"
}
```

### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123!"
}

Response 200:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

## Tickets

All ticket endpoints require `Authorization: Bearer <token>` header.

### List Tickets
```
GET /tickets?skip=0&limit=10

Response 200: [ TicketObject, ... ]
```

### Get Ticket
```
GET /tickets/{id}

Response 200: TicketObject
```

### Create Ticket
```
POST /tickets
Content-Type: application/json

{
  "title": "Device XYZ offline",
  "description": "Device has been offline since 08:00",
  "priority": "high",
  "device_id": "DEV-001",
  "location": "Ward B"
}

Response 201: TicketObject
```

### Update Ticket
```
PATCH /tickets/{id}
Content-Type: application/json

{
  "status": "in_progress",
  "assignee_id": 2
}

Response 200: TicketObject
```

### Delete Ticket
```
DELETE /tickets/{id}

Response 204
```

### Analyze Ticket (RCA)
```
POST /tickets/{id}/analyze
Content-Type: application/json

{
  "context": "Device was restarted twice before going offline"
}

Response 200:
{
  "ticket_id": 1,
  "suggestions": [
    {
      "cause": "Power supply failure",
      "confidence": 0.87,
      "resolution": "Replace PSU or check power cable",
      "similar_incidents": ["TKT-023", "TKT-045"]
    }
  ]
}
```

## Health

```
GET /health

Response 200: { "status": "ok" }
```
