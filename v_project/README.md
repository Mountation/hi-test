# v_project (Vue 3 + Element Plus frontend)

This is a separate frontend for the AI评测系统. It replicates the UI and interactions implemented in Django templates under `myapp/templates/` and calls the existing Django endpoints.

Quick start

1. Install dependencies

```powershell
cd v_project
npm install
```

2. Run dev server

```powershell
npm run dev
```

Notes

- The dev server proxies requests to `http://localhost:8000` by default. Make sure your Django backend is running there.
- The frontend expects the same endpoints as in the Django app (e.g., `/datasets/`, `/datasets/create/`, `/datasets/delete/:id/`, `/run_evaluation/`, `/evaluation/status/`, `/evaluation/cancel/`).
- CSRF: the API service will read a CSRF token from a DOM element named `csrfmiddlewaretoken` when present. For local development you can configure Django to accept the dev server origin or use the proxy.

Next steps

- Improve error handling and add more UI polish.
- Add unit tests and TypeScript if desired.
