# Security and limitations

This application is an educational proof of concept. Report security concerns privately through GitHub's repository security advisory if available, not by publishing secret tokens in an issue.

- Keep `OPENAQ_API_KEY` in server-side environment variables. Never put it in `VITE_` browser variables.
- The demo does not provide an authenticated, multi-tenant production environment.
- Restrict CORS origins and apply rate limiting and TLS before public hosting.
- Only load trusted `.joblib` files (pickle-based deserialization may execute untrusted code).
- No medical, emergency, or official AQI recommendations should be derived from the sample forecasts.
- Sample datasets are synthetic; source provenance should be clearly displayed when using live public data.
