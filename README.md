# Talent Intelligence

AI-powered Talent Intelligence Platform for discovering, indexing, searching, and ranking software engineers using Artificial Intelligence.

## 🚀 Overview

Talent Intelligence is an AI platform designed to automate many of the tasks traditionally performed by technical recruiters.

Instead of manually searching through hundreds of profiles, the platform continuously collects public candidate information, enriches it with AI, and enables semantic search across the entire talent database.

## Features

- 🔍 Search candidates by technologies
- 🤖 AI-powered profile analysis
- 🧠 Automatic skill extraction
- 📊 Candidate ranking
- 🔎 Semantic search using vector embeddings
- 📄 CV parsing
- 🌍 Multi-source profile indexing
- 📈 Recruiter dashboard
- 💬 Natural language search

## Example Searches

```
Senior Python Django developer in Peru
```

```
Backend Engineer with AWS and Docker
```

```
Find candidates similar to this profile
```

## Architecture

```
                AI Agent
                    │
     ┌──────────────┼──────────────┐
     │              │              │
 LinkedIn       GitHub         CV Parser
     │              │              │
     └──────────────┼──────────────┘
                    │
            Profile Normalizer
                    │
         Embeddings + Skill Extraction
                    │
          PostgreSQL + pgvector
                    │
            Semantic Search API
```

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- Celery
- Redis

### Database

- PostgreSQL
- pgvector

### AI

- OpenAI
- LangGraph
- LangChain

### Frontend

- Vue.js
- TailwindCSS

### Infrastructure

- Docker
- GitHub Actions

## Roadmap

- [ ] Project setup
- [ ] Django backend
- [ ] Authentication
- [ ] PostgreSQL
- [ ] AI Skill Extractor
- [ ] Embeddings
- [ ] Candidate Search
- [ ] Dashboard
- [ ] Recruiter Chat
- [ ] CV Import
- [ ] GitHub Import
- [ ] LinkedIn Connector (where permitted by platform policies)

## License

MIT