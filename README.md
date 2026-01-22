# Blog API

A RESTful API built with Django REST framework, featuring JWT-based authentication and author-based access control.

---

## Features

- JWT-based authentication
- Anonymous users have read-only access to published posts
- Authenticated users can create posts and update and delete their own posts
- Unpublished posts only visible to their authors
- Paginated post listing


## Installation

```bash
git clone https://github.com/Esat-cpu/blog_api.git
cd blog_api
uv venv && source .venv/bin/activate
uv sync
```

Create a `.env` file based on the `.env.example` file and configure the required environment variables.

```bash
uv run manage.py migrate
uv run manage.py runserver
```
