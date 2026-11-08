# StratifyIQ API reference

Base URL: `http://127.0.0.1:8000`. Interactive docs are served at `/docs`. Every endpoint except `/health`, `/auth/signup`, `/auth/login`, `/auth/accept-invite` and `/auth/forgot-password` requires `Authorization: Bearer <token>`.

| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | /auth/signup | public | Create company and Admin account; returns token |
| POST | /auth/login | public | Email and password login |
| GET | /auth/me | any | Current user |
| POST | /auth/invite | admin | Invite a Manager; returns single-use token |
| POST | /auth/accept-invite | public | Activate an invite; returns token |
| POST | /auth/forgot-password | public | Stub; generic response |
| GET | /company | any | Company details |
| POST / GET | /departments | write / any | Create or list departments |
| POST / GET | /teams | write / any | Create or list teams |
| POST / GET | /employees | write / any | Create or list employees with skills and availability |
| GET | /employees/workload | any | Utilisation per employee (4-week horizon) |
| POST / GET | /projects | write / any | Create or list projects |
| GET | /projects/{id} | any | Project detail |
| PATCH | /projects/{id}/budget | write | Set or reallocate project budget |
| PATCH | /projects/{id}/progress | write | Update progress percentage |
| POST / GET | /projects/{id}/tasks | write / any | Create or list tasks and milestones |
| PATCH | /tasks/{id} | write | Mark done or reassign |
| POST | /projects/{id}/expenses | write | Record an expense |
| GET | /projects/{id}/budget | any | Budget, spent, remaining, burn ratio, over-budget flag |
| GET | /analytics/projects/{id}/predict | any | Snapshot, predictions, risk level, health |
| POST | /analytics/projects/{id}/simulate | any | Run a what-if decision; body `{action, value}` |
| GET | /analytics/projects/{id}/recommend | any | Top three ranked decisions against do-nothing |
| GET | /analytics/dashboard | any | Business health, per-project risk, high-risk list |

Simulator actions: `hire_employee` (value = number of hires), `increase_budget` (amount), `reduce_budget` (amount), `extend_deadline` (days), `reduce_scope` (percent), `reallocate_resources` (value ignored).

Write roles are `admin` and `manager`. Any write by any other role returns 403, and any record outside the caller's company returns 404.
