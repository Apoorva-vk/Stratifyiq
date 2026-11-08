# StratifyIQ UML diagrams

These diagrams use Mermaid. They render on GitHub, and in VS Code with a Mermaid extension.

## 1. Use case diagram

```mermaid
flowchart LR
    Admin((Admin))
    Manager((Manager))
    Visitor((New user))

    subgraph StratifyIQ
        UC1[Sign up and confirm email]
        UC2[Log in and reset password]
        UC3[Invite a manager]
        UC4[Manage projects, tasks and milestones]
        UC5[Manage team and organisation]
        UC6[Record expenses and budget]
        UC7[Simulate a decision]
        UC8[View recommendations and forecasts]
        UC9[View dashboards and alerts]
        UC10[Download and email reports]
        UC11[Ask the assistant]
    end

    Visitor --> UC1
    Admin --> UC2
    Manager --> UC2
    Admin --> UC3
    Admin --> UC5
    Admin --> UC4
    Manager --> UC4
    Manager --> UC6
    Admin --> UC6
    Admin --> UC7
    Manager --> UC7
    Admin --> UC8
    Manager --> UC8
    Admin --> UC9
    Manager --> UC9
    Admin --> UC10
    Manager --> UC10
    Admin --> UC11
    Manager --> UC11
```

## 2. Class diagram (main data model)

```mermaid
classDiagram
    class Company {
        +int id
        +string name
    }
    class User {
        +int id
        +string email
        +string role
        +bool is_active
    }
    class Department {
        +int id
        +string name
    }
    class Team {
        +int id
        +string name
    }
    class Employee {
        +int id
        +string name
        +string skills
        +float capacity_hours
        +float availability_pct
    }
    class Project {
        +int id
        +string name
        +float budget
        +date deadline
        +float progress
    }
    class Task {
        +int id
        +float estimated_hours
        +string milestone
        +bool done
    }
    class Expense {
        +float amount
        +date incurred_on
    }
    class MilestoneDate {
        +string name
        +date due_date
    }
    class DecisionRecord {
        +string action
        +float scenario_delay
        +bool outcome_late
    }
    class HealthSnapshot {
        +date week_start
        +float overall
    }

    Company "1" --> "*" User
    Company "1" --> "*" Department
    Department "1" --> "*" Team
    Team "1" --> "*" Employee
    Company "1" --> "*" Project
    Project "1" --> "*" Task
    Project "1" --> "*" Expense
    Project "1" --> "*" MilestoneDate
    Employee "0..1" --> "*" Task : assigned
    Project "1" --> "*" DecisionRecord
    Project "1" --> "*" HealthSnapshot
```

## 3. Sequence diagram: simulating a decision

```mermaid
sequenceDiagram
    actor M as Manager
    participant UI as React frontend
    participant API as FastAPI
    participant DB as PostgreSQL
    participant ML as Prediction models

    M->>UI: Choose project and decision, press Run
    UI->>API: POST /analytics/projects/{id}/simulate (JWT)
    API->>API: Verify token and company
    API->>DB: Read project, tasks, expenses
    DB-->>API: Project data
    API->>ML: Predict baseline
    API->>API: Apply decision to a copy of the data
    API->>ML: Predict after decision
    ML-->>API: Delay risk, success, overrun
    API-->>UI: Before, after and difference (nothing saved)
    UI-->>M: Show comparison
```

## 4. Sequence diagram: sign-up with email confirmation

```mermaid
sequenceDiagram
    actor U as New user
    participant UI as React frontend
    participant API as FastAPI
    participant DB as PostgreSQL
    participant MAIL as Email (SMTP)

    U->>UI: Fill in sign-up form
    UI->>API: POST /auth/signup
    API->>DB: Create company, admin, pending verification
    API->>MAIL: Send confirmation link
    API-->>UI: Account created (login blocked until confirmed)
    U->>UI: Open confirmation link, press Confirm
    UI->>API: POST /auth/verify
    API->>DB: Remove pending verification
    U->>UI: Log in
    UI->>API: POST /auth/login
    API-->>UI: JWT token
```
