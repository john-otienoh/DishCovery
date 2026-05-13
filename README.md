# DishCovery API

A recipe sharing REST API built with **Django 5** and **Django REST Framework**.

---

## Features

- **JWT Authentication** — register, login, token refresh, logout with blacklisting
- **Recipe CRUD** — create, read, update, delete recipes with rich metadata
- **Advanced Search & Filtering** — full-text search + filter by cuisine, difficulty, calories, time, tags, meal type, rating
- **Ratings** — one rating per user per recipe; recipe aggregate auto-updated via signals
- **Comments** — nested replies, edit/delete own comments
- **Saved Recipes** — toggle save/unsave a recipe to your personal collection
- **Social Follows** — follow/unfollow users; denormalised counts for performance
- **Shares** — log share events per platform (WhatsApp, Twitter, email, …)
- **Notifications** — activity feed for follows, comments, and ratings
- **Auto-generated Swagger UI** at `/api/docs/`
- **Seed command** — one-command DB population from `recipes.json`

---

## Tech Stack

| Layer           | Technology                              |
|-----------------|------------------------------------------|
| Framework       | Django 5, Django REST Framework 3.15     |
| Auth            | djangorestframework-simplejwt            |
| API Docs        | drf-spectacular (OpenAPI 3 / Swagger)    |
| Filtering       | django-filter                            |
| CORS            | django-cors-headers                      |
| Database (dev)  | SQLite                                   |
| Database (prod) | PostgreSQL                               |
| Static files    | WhiteNoise                               |
| WSGI server     | Gunicorn                                 |

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd dishcovery

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY

# 5. Run migrations
python manage.py migrate

# 6. Seed the database from recipes.json
python manage.py seed_recipes

# 7. (Optional) Create a superuser
python manage.py createsuperuser

# 8. Start the dev server
python manage.py runserver
```

Open **http://127.0.0.1:8000/api/docs/** to explore the interactive Swagger UI.

---

## API Endpoints

### Auth  `POST`
| Endpoint | Description |
|---|---|
| `/api/v1/auth/register/` | Create account; returns JWT pair |
| `/api/v1/auth/login/` | Login; returns JWT pair + user |
| `/api/v1/auth/logout/` | Blacklist refresh token |
| `/api/v1/auth/token/refresh/` | Refresh access token |
| `/api/v1/auth/change-password/` | Change own password |

### Users
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/users/` | Search users |
| GET/PUT/PATCH | `/api/v1/users/me/` | Own profile |
| GET | `/api/v1/users/<username>/` | Public profile |
| POST | `/api/v1/users/<username>/follow/` | Follow / unfollow |
| GET | `/api/v1/users/<username>/followers/` | Follower list |
| GET | `/api/v1/users/<username>/following/` | Following list |

### Recipes
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/recipes/` | List/search recipes |
| POST | `/api/v1/recipes/` | Create recipe |
| GET | `/api/v1/recipes/<id>/` | Recipe detail |
| PUT/PATCH | `/api/v1/recipes/<id>/` | Update (author only) |
| DELETE | `/api/v1/recipes/<id>/` | Delete (author only) |
| GET | `/api/v1/recipes/by/<username>/` | Recipes by user |
| GET | `/api/v1/recipes/cuisines/` | Distinct cuisines |
| GET | `/api/v1/recipes/tags/` | All tags |
| GET | `/api/v1/recipes/meal-types/` | All meal types |

#### Recipe search query params
```
?search=chicken          full-text search
?cuisine=Italian
?difficulty=Easy|Medium|Hard
?min_calories=100
?max_calories=500
?max_time=30             prep + cook ≤ 30 min
?meal_type=Dinner
?tag=Pasta
?min_rating=4
?author=johndoe
?ordering=-rating        sort by rating desc
```

### Interactions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/interactions/recipes/<id>/rate/` | Rate a recipe (1-5) |
| DELETE | `/api/v1/interactions/recipes/<id>/rate/` | Remove your rating |
| GET | `/api/v1/interactions/recipes/<id>/ratings/` | All ratings |
| GET | `/api/v1/interactions/recipes/<id>/comments/` | Comments + replies |
| POST | `/api/v1/interactions/recipes/<id>/comments/` | Post comment |
| GET/PATCH/DELETE | `/api/v1/interactions/comments/<id>/` | Comment detail |
| POST | `/api/v1/interactions/recipes/<id>/save/` | Save / unsave recipe |
| GET | `/api/v1/interactions/saved/` | My saved recipes |
| POST | `/api/v1/interactions/recipes/<id>/share/` | Log a share |

### Notifications
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/notifications/` | All notifications (`?unread=true`) |
| GET | `/api/v1/notifications/unread-count/` | Badge count |
| POST | `/api/v1/notifications/mark-read/` | Mark read (`{"ids":[…]}` or all) |
| GET/DELETE | `/api/v1/notifications/<id>/` | Single notification |

---

## Project Structure

```
dishcovery/
├── manage.py
├── requirements.txt
├── .env.example
├── scripts/
│   └── recipes.json          # seed data
├── dishcovery/               # project package
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── users/                # custom User, Follow, auth views
    ├── recipes/              # Recipe, Tag, MealType + seed command
    ├── interactions/         # Rating, Comment, SavedRecipe, Share
    └── notifications/        # Notification model + service
```

---

## Deployment Checklist

1. Set `DJANGO_ENV=production` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure PostgreSQL credentials
4. Set `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
5. Run `python manage.py collectstatic`
6. Use `gunicorn dishcovery.wsgi:application` behind nginx/caddy

---

## Running Tests

```bash
python manage.py test
```

---

## API Documentation

- **Swagger UI** → http://localhost:8000/api/docs/
- **ReDoc** → http://localhost:8000/api/redoc/
- **OpenAPI schema** → http://localhost:8000/api/schema/