Deployment and packaging instructions

Docker (backend + frontend):

- Build and start locally:

```
docker-compose up -d --build
```

- Backend will be available on http://localhost:8000
- Frontend will be available on http://localhost:3000

Secrets & runtime configuration

- Copy `.env.example` to `.env` locally for development and fill secrets.
- For production, supply secrets via environment variables or a secrets manager. Example with Vault:

```
export VAULT_ADDR=https://vault.example.com
export VAULT_TOKEN=...
docker-compose up -d --build
```

The application uses `achillesoracle.settings.Settings` to load config from env or `.env`. It can also fetch secrets from Vault if `VAULT_ADDR` and `VAULT_TOKEN` are set.

Package (Python wheel / sdist):

```
python -m build
```

This will create artifacts in the `dist/` folder usable for PyPI or internal package distribution.

CI:

See `.github/workflows/ci.yml` for a basic workflow that runs tests and builds Docker images on push.
