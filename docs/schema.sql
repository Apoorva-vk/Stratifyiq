-- StratifyIQ PostgreSQL schema (matches app/models.py)
CREATE TABLE companies (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id             SERIAL PRIMARY KEY,
    company_id     INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email          VARCHAR(255) NOT NULL UNIQUE,
    full_name      VARCHAR(200) NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    role           VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager')),
    is_active      BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX ix_users_company ON users(company_id);

CREATE TABLE invites (
    id          SERIAL PRIMARY KEY,
    company_id  INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email       VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL DEFAULT 'manager' CHECK (role IN ('manager')),
    token       VARCHAR(64) NOT NULL UNIQUE,
    accepted    BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at  TIMESTAMP NOT NULL
);

CREATE TABLE departments (
    id          SERIAL PRIMARY KEY,
    company_id  INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name        VARCHAR(150) NOT NULL
);

CREATE TABLE teams (
    id             SERIAL PRIMARY KEY,
    company_id     INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    department_id  INT NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    name           VARCHAR(150) NOT NULL
);

CREATE TABLE employees (
    id                 SERIAL PRIMARY KEY,
    company_id         INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    team_id            INT REFERENCES teams(id) ON DELETE SET NULL,
    name               VARCHAR(150) NOT NULL,
    title              VARCHAR(150) NOT NULL,
    skills             TEXT NOT NULL DEFAULT '',
    experience_years   DOUBLE PRECISION NOT NULL DEFAULT 0,
    capacity_hours     DOUBLE PRECISION NOT NULL DEFAULT 40,
    availability_pct   DOUBLE PRECISION NOT NULL DEFAULT 100 CHECK (availability_pct BETWEEN 0 AND 100),
    hourly_cost        DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE TABLE projects (
    id           SERIAL PRIMARY KEY,
    company_id   INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name         VARCHAR(200) NOT NULL,
    budget       DOUBLE PRECISION NOT NULL CHECK (budget > 0),
    start_date   DATE NOT NULL,
    deadline     DATE NOT NULL,
    scope_units  DOUBLE PRECISION NOT NULL DEFAULT 100,
    progress     DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    status       VARCHAR(20) NOT NULL DEFAULT 'active',
    CHECK (deadline > start_date)
);

CREATE TABLE tasks (
    id               SERIAL PRIMARY KEY,
    project_id       INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title            VARCHAR(200) NOT NULL,
    estimated_hours  DOUBLE PRECISION NOT NULL CHECK (estimated_hours > 0),
    assignee_id      INT REFERENCES employees(id) ON DELETE SET NULL,
    milestone        VARCHAR(200),
    done             BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE expenses (
    id           SERIAL PRIMARY KEY,
    project_id   INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    description  VARCHAR(200) NOT NULL,
    amount       DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    incurred_on  DATE NOT NULL
);
