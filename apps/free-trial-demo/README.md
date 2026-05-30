# Governed Delivery Free Trial Demo

## Purpose

This is a dependency-light static demo for the governed delivery agent concept.

It is designed to make the free trial value obvious:

```text
Paste messy intake
→ detect governance risk
→ detect platforms
→ show launch blockers
→ preview generated tickets
→ preview evidence packet
→ download sample exports
```

## Run Locally

From this folder:

```bash
python -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

You can also use:

```bash
npm run start
```

## Important Safety Rule

Do not paste real PHI, PCI, credentials, secrets, or live client data. Use synthetic, redacted, or generalized intake text.

## Current State

This demo is intentionally front-end only. It mirrors the generated package concept without requiring a backend server.

The next production step would be to wrap `tools/generate_governed_delivery_package.py` behind a backend API route and return real generated outputs.
