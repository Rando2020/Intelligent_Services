# Governed Delivery Free Trial Demo

## Purpose

This is a dependency-light static demo for the governed delivery agent concept.

It is designed to make the free trial value obvious:

```text
Paste messy intake
→ call backend API
→ run YAML rules and platform profiles
→ show launch blockers
→ preview generated tickets
→ preview evidence packet
→ download real generated exports when backend is running
```

## Run with Real Backend Analysis

From the repository root, start the backend API:

```bash
python apps/backend-demo-api/server.py
```

Then in a second terminal, start the static demo:

```bash
cd apps/free-trial-demo
python -m http.server 4173
```

Open:

```text
http://localhost:4173
```

The app calls:

```text
http://localhost:8787/api/analyze
```

## Backend Fallback Behavior

If the backend API is not running, the app falls back to a local client-side preview so the UI remains demoable.

The fallback is useful for showing the flow, but the real package generation comes from the backend API.

## Custom Backend URL

Before loading the app, set:

```html
<script>
  window.GOVERNED_DELIVERY_API_URL = "https://your-demo-api.example.com/api/analyze";
</script>
```

The static app will use that value instead of localhost.

## Important Safety Rule

Do not paste real PHI, PCI, credentials, secrets, or live client data. Use synthetic, redacted, or generalized intake text.

## Current State

The demo now uses backend-first analysis with local fallback.

Next production step:

```text
Deploy the backend API and static demo together, add auth/rate limits, and persist only approved non-sensitive exports.
```
