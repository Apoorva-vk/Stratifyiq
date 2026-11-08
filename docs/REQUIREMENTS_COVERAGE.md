# Requirements coverage

| Module | Requirement | Status | Where |
|---|---|---|---|
| 1 Authentication | Login, signup, forgot password | Done | Auth screen; `/auth/*` |
| | Email confirmation at sign-up | Done | `/auth/verify` |
| | JWT, role-based access (Admin, Manager) | Done | `app/deps.py` |
| 2 Company workspace | Company profile | Done | Organisation page |
| | Departments, teams | Done | Organisation page |
| 3 Employees | Details, skills, experience, availability | Done | Team page |
| | Workload and utilisation | Done | Team page, `/employees/workload` |
| 4 Projects | Projects, tasks | Done | Projects page |
| | Milestones with dates | Done | Milestones panel |
| | Deadlines (project and task) | Done | Projects, task due dates, overdue alerts |
| | Progress tracking | Done | Manual, or "Use task completion" |
| 5 Budget | Allocation, expenses, forecasting | Done | Projects → Manage, forecast chart |
| 6 Decision simulator | Six decisions, predicted before acting | Done | Simulator; combined scenarios |
| 7 Prediction engine | Delay risk, success, overrun, utilisation | Done | Trained on synthetic data (state in report) |
| 8 Recommendation engine | Budget, timeline, risk mitigation | Done | Recommendations |
| | Best resource allocation | Done | Allocation suggestions; assignee suggestions |
| 9 Dashboards | Executive, employee, project, budget, risk, decision | Done | In-app dashboards and Insights |
| | Power BI dashboards | Partly | CSV exports and guide; the .pbix file is built by you in Power BI Desktop |
| 10 Notifications | Budget, deadline, overload, high risk | Done | Alerts panel |
| 11 Reports | PDF, Excel | Done | Reports page |
| | Weekly and monthly reports | Done | On demand, emailed, and scheduled by Task Scheduler (`docs/SCHEDULED_REPORTS.md`) |
| 12 Health score | Overall, project, financial, employee, risk | Done | Dashboard rings |

## Future enhancements (listed in the spec)

| Item | Status |
|---|---|
| AI chat assistant | Done (rule-based, with optional local AI model) |
| Voice commands | Done (browser speech, Chrome or Edge) |
| Predictive resource allocation | Partly (suggestions, not forecasts) |
| Jira, GitHub, Teams, Slack integration | Not built; future work |
| Mobile application | Not built; the web app works in a mobile browser |
| Cloud deployment (Azure or Render) | Not built; future work |

## Technology stack

| Item | Status |
|---|---|
| React, FastAPI, Python, PostgreSQL | Used |
| Scikit-learn, NumPy | Used (pandas was removed because nothing used it) |
| JWT | Used |
| Power BI | Connected through CSV exports |
| Git and GitHub | Set up with `docs/GIT_SETUP.md` (you run the commands) |
| Postman | Collection in `docs/StratifyIQ.postman_collection.json` |

## Documentation

| Item | Status |
|---|---|
| Architecture and ER diagram | Done (`docs/ARCHITECTURE.md`) |
| UML diagrams (use case, class, sequence) | Done (`docs/UML.md`) |
| Wireframes and UI design | Screenshots of the running app can serve as wireframes; a separate design document is not built |
| Demo and viva guide | Done |
| Research paper | Not written; needs your input and university format |
| Project report | Not written; the existing documents provide the material |
