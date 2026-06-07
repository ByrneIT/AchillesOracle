Deployment and packaging instructions

Docker (backend + frontend):

- Build and start locally:

```
docker-compose up -d --build
```

- Backend will be available on http://localhost:8000
- Frontend will be available on http://localhost:3000

Package (Python wheel / sdist):

```
python -m build
```

This will create artifacts in the `dist/` folder usable for PyPI or internal package distribution.

CI:

See `.github/workflows/ci.yml` for a basic workflow that runs tests and builds Docker images on push.
