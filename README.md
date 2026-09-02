# Vivaha

Vivaha is a Django matrimonial platform for creating detailed profiles, discovering compatible matches, and building meaningful connections.

## Features

- Email-based custom user authentication
- Matrimonial profiles with education, profession, family, lifestyle, and partner preferences
- Profile photos with validation and primary-photo management
- Profile completion scoring
- Discovery search, filters, and compatibility scoring
- Interests with send, accept, reject, and cancel workflows
- Favorites and shortlist management
- Block, unblock, and report workflows
- Conversations unlocked by accepted interests
- AJAX messaging without page reloads
- Unread message counts and automatic notification read state
- Responsive mobile and desktop interface
- Django admin support for moderation and management

## Technology

- Python 3.14+
- Django 6.1
- SQLite for development
- PostgreSQL-ready configuration for production
- Pillow for image validation and generated demo photos
- django-filter for discovery filters

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd matrimony
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements/development.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and update the secret key and settings:

```powershell
Copy-Item .env.example .env
```

The development project uses SQLite by default. Set `DATABASE_URL` only when using PostgreSQL.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. The admin dashboard is available at <http://127.0.0.1:8000/admin/>.

## Demo Data

To replace non-admin development data with 25 complete Bangladeshi demo profiles and generated approved photos:

```bash
python manage.py seed_bangladeshi_profiles --reset
```

The command preserves existing superusers. Demo accounts receive the default password shown by the command. Do not use demo credentials in production.

## Testing

Run the complete test suite:

```bash
python manage.py test
```

Run Django configuration checks:

```bash
python manage.py check
```

## Project Structure

```text
apps/
  accounts/       Custom user model and authentication
  connections/    Interests, favorites, blocks, and reports
  core/           Landing page, dashboard, shared utilities, demo commands
  discovery/      Search, filters, and match scoring
  messaging/      Conversations, messages, and notifications
  profiles/       Profiles, details, photos, and completion scoring
config/
  settings/       Base, development, and production settings
docs/             Implementation plan and task tracker
static/           CSS, JavaScript, and static images
templates/        Project-wide Django templates
```

## Security Notes

- Keep `.env` out of version control.
- Use a unique production `SECRET_KEY`.
- Configure `ALLOWED_HOSTS`, HTTPS, secure cookies, and PostgreSQL before deployment.
- Do not use generated demo passwords in a deployed environment.
- User-uploaded media should be stored outside the repository in production.

## Project Status

Foundation, profiles, discovery, connections, communication, notifications, responsive layouts, and development demo data are implemented. Trust and safety moderation and production hardening remain ongoing areas tracked in [docs/task.md](docs/task.md).

## License

No license has been selected for this project yet. Add a license before distributing the repository publicly.
