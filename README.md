# Talent Intelligence

Talent Intelligence is a recruiter-focused platform for **registering, searching, organizing, and managing software engineering candidates**.

The platform is being developed incrementally. The first MVP focuses on solving the core recruiter workflow with structured candidate data and deterministic search. AI-powered capabilities will be introduced after the core workflow is validated.

---

## 🚀 Vision

Talent Intelligence aims to evolve into an AI-powered Talent Intelligence Platform capable of discovering, indexing, enriching, searching, and ranking software engineering talent.

The long-term vision includes:

* AI-powered profile analysis
* Automatic skill extraction
* Semantic candidate search
* Candidate ranking and matching
* CV parsing
* Multi-source profile indexing
* Natural language recruiter search

However, these capabilities are intentionally being developed **after the core recruiter workflow**.

---

## 🎯 MVP

The first MVP focuses on a simple and useful recruiter workflow:

```text
Register candidate
       │
       ▼
Search candidates
       │
       ▼
Filter candidates
       │
       ▼
Review candidate profile
       │
       ├── Favorite
       ├── Add notes
       └── Change status
               │
               ▼
          Recruiter Dashboard
```

The MVP allows recruiters to:

* Register candidates
* Manage candidate profiles
* Associate skills
* Register experience
* Register education
* Assign country and city
* Search candidates
* Filter candidates by skills
* Filter candidates by multiple skills
* Filter candidates by city
* Filter candidates by country
* Combine multiple filters
* Paginate results
* Order results
* Save candidates as favorites
* Add recruiter notes
* Manage candidate pipeline/status
* View recruiter metrics through a dashboard

---

## 🔍 Candidate Search

The initial search engine is intentionally **deterministic and based on structured data**.

Supported search capabilities include:

```text
GET /api/candidates/
```

### Search

```text
/api/candidates/?search=python
```

Searches across:

* First name
* Last name
* Email
* Headline
* Summary

### Skills

```text
/api/candidates/?skills=python,django
```

Multiple skills use **AND logic**.

For example:

```text
skills=python,django,aws
```

returns candidates that have **all three skills**.

### Location

Search by city:

```text
/api/candidates/?city=Lima
```

Search by country:

```text
/api/candidates/?country=PE
```

Filters can also be combined:

```text
/api/candidates/?skills=python,django&city=Lima
```

### Pagination

Candidate results are paginated to support large candidate databases.

### Ordering

Candidates can be ordered using supported fields:

```text
/api/candidates/?ordering=-created_at
```

---

## 👤 Candidate Profile

A candidate can contain:

```text
Candidate
├── Personal information
├── Location
│   ├── Country
│   └── City
├── Skills
├── Experience
└── Education
```

This structured model provides the foundation for future AI-powered enrichment and semantic search.

---

## ⭐ Recruiter Workflow

The next MVP capabilities focus on allowing recruiters to manage candidates throughout the recruitment process.

### Favorites

Recruiters will be able to save interesting candidates for later review.

```text
POST   /api/candidates/{id}/favorite/
DELETE /api/candidates/{id}/favorite/
GET    /api/candidates/favorites/
```

### Notes

Recruiters will be able to attach private notes to candidates.

Example:

```text
"Strong Python/Django profile.
Good experience leading backend teams."
```

### Candidate Pipeline

Candidates will eventually move through a recruitment workflow such as:

```text
NEW
  ↓
SCREENING
  ↓
INTERVIEW
  ↓
OFFER
  ↓
HIRED
```

Candidates can also be marked as:

```text
REJECTED
```

---

## 📊 Recruiter Dashboard

The dashboard will provide an overview of the recruiter's candidate pipeline.

Example:

```text
Candidates             1,248

New                      143
Screening                 82
Interview                 31
Offer                      8
Hired                     14
```

Future dashboard metrics will include:

* Candidates by status
* Candidates by skill
* Candidates by country
* Candidates by city
* Favorite candidates
* Recently added candidates
* Recruitment pipeline metrics

---

## 🤖 AI & Intelligence

AI capabilities are intentionally part of the **second phase** of the project.

### AI Skill Extractor

Automatically extract skills from candidate information such as:

```text
Senior Backend Engineer with
Python, Django, PostgreSQL and AWS
```

Result:

```text
Python
Django
PostgreSQL
AWS
```

### Embeddings

Generate vector representations of candidate profiles using PostgreSQL + pgvector.

### Semantic Search

Enable queries such as:

```text
Senior Python Django developer in Peru
```

or:

```text
Backend Engineer with AWS and Docker
```

without requiring exact keyword matches.

### Candidate Matching

Future versions will be able to identify candidates similar to a reference profile.

---

## 📄 Candidate Import

Future candidate ingestion capabilities include:

* CV Import
* GitHub Import
* LinkedIn Connector
* Public profile indexing

LinkedIn integrations will only be implemented where permitted by applicable platform policies.

---

## 🏗 Architecture

### Current MVP

```text
                    Recruiter
                        │
                        ▼
                Django REST API
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     Candidates      Skills       Locations
          │
     ┌────┼────┬──────────┐
     ▼    ▼    ▼          ▼
 Experience Education Favorites Notes
          │
          ▼
      PostgreSQL
```

### Future AI Architecture

```text
                    AI Agents
                        │
          ┌─────────────┼─────────────┐
          │             │             │
       GitHub          CV          LinkedIn
          │             │             │
          └─────────────┼─────────────┘
                        ▼
              Profile Normalizer
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       Skill Extraction       Embeddings
             │                     │
             └──────────┬──────────┘
                        ▼
                 PostgreSQL
                   + pgvector
                        │
                        ▼
              Semantic Search API
                        │
                        ▼
              Recruiter Experience
```

---

## 🛠 Tech Stack

### Backend

* Python
* Django
* Django REST Framework
* Celery
* Redis

### Database

* PostgreSQL
* pgvector

### AI

* OpenAI
* LangGraph
* LangChain

### Frontend

* Vue.js
* TailwindCSS

### Infrastructure

* Docker
* GitHub Actions

---

## 🗺 Roadmap

### Foundation

- [x] Project setup
- [x] Django backend
- [x] PostgreSQL
- [x] Django REST Framework
- [x] Swagger / OpenAPI
- [x] Core app
- [x] Health endpoint
- [x] Docker / Docker Compose
- [x] Testing infrastructure
- [x] Ruff / code quality

### Authentication & Users

- [x] Authentication
- [x] Custom User model
- [x] User registration
- [x] JWT authentication
- [x] User profile
- [x] Logout / token revocation

### Candidate Management

- [x] Candidate management
- [x] Skills management
- [x] Experience management
- [x] Education management
- [x] Candidate ↔ Skills
- [x] Candidate ↔ Experience
- [x] Candidate ↔ Education
- [x] Candidate favorites
- [x] Candidate notes

### Locations

- [x] Country management
- [x] City management
- [x] Country → City relationship
- [x] Country / City fixtures
- [x] Candidate location
- [x] Location API

### Candidate Search

- [x] Candidate search
- [x] Search by name
- [x] Search by email
- [x] Search by headline / summary
- [x] Filter by skill
- [x] Filter by multiple skills
- [x] Multiple skills with AND logic
- [x] Filter by city
- [x] Filter by country
- [x] Combined filters
- [x] Pagination
- [x] Ordering

### Organizations & Recruiters

- [x] Organization management
- [x] User ↔ Organization relationship
- [x] Recruiter management
- [x] Organization-based access control
- [x] Recruiter isolation by organization

### Jobs & Recruiter Workflow

- [x] Job management
- [x] Job status
- [x] Employment type
- [x] Work mode
- [x] Job location
- [x] Remote jobs without city
- [x] Hybrid / on-site jobs with city
- [x] Job skills
- [x] Job search / filtering
- [x] Job ordering
- [x] Organization job isolation

### Applications

- [x] Candidate applications
- [x] Application uniqueness per candidate / job
- [x] List applications by job
- [x] Create application
- [x] Application status
- [x] Application pipeline
- [x] Pipeline transition validation
- [x] Organization isolation
- [x] Application history
- [ ] Application notes
- [ ] Recruiter workflow
- [ ] Recruiter dashboard

### AI & Intelligence

- [ ] AI Skill Extractor
- [ ] Embeddings
- [ ] Semantic Candidate Search
- [ ] Candidate matching
- [ ] Candidate ranking / scoring
- [ ] Recruiter Chat

### Candidate Import

- [ ] CV Import
- [ ] GitHub Import
- [ ] LinkedIn Connector (where permitted by platform policies)

### Production

- [ ] Database indexes / query optimization
- [ ] Caching
- [ ] Rate limiting
- [ ] Structured logging
- [ ] Observability
- [ ] CI/CD
- [ ] Production deployment
- [ ] Security hardening

---

## 🧪 Development

Run the test suite with:

```bash
docker compose run --rm backend pytest
```

The project follows a test-first approach for API and business functionality.

---

## 📜 License

MIT
