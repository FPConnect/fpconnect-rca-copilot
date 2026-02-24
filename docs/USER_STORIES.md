# User Stories — MVP

## US-01: User Registration
**As a** new technician,  
**I want to** register an account,  
**So that** I can access the system.

**Acceptance Criteria:**
- POST /auth/register returns 201 with user object
- Password is hashed (not stored in plaintext)
- Duplicate email returns 400

## US-02: User Login
**As a** registered user,  
**I want to** log in with email/password,  
**So that** I receive a JWT token.

**Acceptance Criteria:**
- POST /auth/login returns 200 with access_token
- Invalid credentials return 401

## US-03: Create Ticket
**As a** technician,  
**I want to** create a support ticket,  
**So that** I can track a device issue.

**Acceptance Criteria:**
- POST /tickets returns 201 with ticket object
- Requires authentication

## US-04: List Tickets
**As a** manager,  
**I want to** view all tickets,  
**So that** I can monitor operations.

**Acceptance Criteria:**
- GET /tickets returns paginated list

## US-05: Update Ticket
**As a** technician,  
**I want to** update a ticket's status,  
**So that** the team knows its progress.

**Acceptance Criteria:**
- PATCH /tickets/{id} updates status, priority, assignee

## US-06: RCA Analysis
**As a** technician,  
**I want to** get an RCA suggestion for a ticket,  
**So that** I can resolve it faster.

**Acceptance Criteria:**
- POST /tickets/{id}/analyze returns suggestions
- Suggestions reference similar past incidents

## US-07: View Dashboard
**As a** manager,  
**I want to** see a metrics dashboard,  
**So that** I can track team performance.

**Acceptance Criteria:**
- Shows open/closed ticket counts
- Shows average resolution time

## US-08: KB Article Search
**As a** technician,  
**I want to** search the knowledge base,  
**So that** I find relevant solutions quickly.

## US-09: Mobile Ticket Creation
**As a** field technician,  
**I want to** create tickets from my phone,  
**So that** I can log issues on-site.

## US-10: Role-Based Access
**As an** administrator,  
**I want to** manage user roles,  
**So that** access is controlled.

**Acceptance Criteria:**
- Roles: admin, manager, technician
- Admins can change user roles

## US-11: Ticket History Log
**As a** technician,  
**I want to** view a ticket's change history,  
**So that** I understand what happened.

## US-12: Priority Management
**As a** manager,  
**I want to** set ticket priorities,  
**So that** critical issues are handled first.

## US-13: Assignment
**As a** manager,  
**I want to** assign tickets to technicians,  
**So that** responsibility is clear.

## US-14: Close Ticket
**As a** technician,  
**I want to** close a resolved ticket,  
**So that** the backlog stays clean.

## US-15: Notifications
**As a** user,  
**I want to** be notified when a ticket is assigned to me,  
**So that** I can respond promptly.
