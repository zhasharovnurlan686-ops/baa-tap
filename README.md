# BaaTap KG — Django MVP

Bilingual (Russian/Kyrgyz) MVP for private businesses to publish commercial requests and receive supplier offers. It is **not** a government procurement/tender system.

## Included
- Registration and login; account roles: buyer, supplier, both.
- Company profile, city, phone, public supplier profile.
- Commercial request catalogue with search, category and city filters.
- Request creation/editing; suppliers can submit/update one offer per request.
- Dashboard for own requests and offers.
- Django admin for users, categories, requests and offers.
- PostgreSQL via `DATABASE_URL`, SQLite fallback for local quick start.
- WhiteNoise static files and Render `render.yaml` blueprint.
- Russian and Kyrgyz language toggle for the main interface. Some validation/help text is currently Russian; add translations before a full public launch.

## Local start (Windows PowerShell)

```powershell
cd D:aatap-kg
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations accounts marketplace
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and admin at http://127.0.0.1:8000/admin/.

If PowerShell blocks activation, run once in that terminal: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then activate again.

## PostgreSQL local (optional)

Create a database named `baatap`, then set a connection URL in the current PowerShell session:

```powershell
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/baatap"
$env:DEBUG = "True"
python manage.py migrate
```

The password in the URL must be URL-encoded if it contains special characters. For a local-only SQLite quick start, leave `DATABASE_URL` unset.

## GitHub

Create an empty GitHub repository, then:

```powershell
git init
git add .
git commit -m "Initial BaaTap KG Django MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/baatap-kg.git
git push -u origin main
```

Replace the remote URL with your repository URL.

## Deploy to Render

1. Push the project to GitHub.
2. In Render, choose **New + → Blueprint** and connect the repository containing `render.yaml`.
3. Review resources and apply. The blueprint requests a Render PostgreSQL database and web service; check the current plan, pricing, region and free-tier limits in Render before confirming.
4. Wait for the build/deploy to finish.
5. Open the web service URL. In Render Shell, create an administrator:

```bash
python manage.py createsuperuser
python manage.py seed_categories
```

The build script runs migrations and collects static files. If the database was provisioned after an earlier build, trigger a redeploy after confirming `DATABASE_URL` is set.

## Important before launch
- Use a unique strong `SECRET_KEY`; Render Blueprint generates one.
- Set `DEBUG=False` in production (already in `render.yaml`). Never put secrets in Git.
- Verify database backups, pricing and persistence on the current Render plan.
- Add email verification, password reset email configuration, abuse/rate limiting, privacy policy, terms, consent and contact verification before public commercial use.
- Do not publish private procurement or government tender listings on this MVP. Get local legal advice on the exact business model.
- Uploaded files and payment handling are intentionally not included in this first MVP.
