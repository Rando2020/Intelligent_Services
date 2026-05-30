# Jira Forge Governed Delivery Scaffold

## Purpose

This is the Jira-native scaffold for the Governed Delivery Agent.

It is designed as an Atlassian Forge starting point, not a production Marketplace app yet.

## Intended Jira Experience

Inside Jira, a user should be able to:

1. Open a project page or issue panel.
2. Paste messy intake or use the current Jira issue as context.
3. Call the governed delivery backend API.
4. Preview risk score, launch blockers, detected platform profiles, generated tickets, and evidence requirements.
5. Create Jira issues from approved generated work items.

## Current Scaffold Includes

```text
manifest.yml
package.json
src/index.js
src/resolvers.js
src/static/index.html
src/static/app.js
src/static/styles.css
```

## Local Setup Concept

Install Forge CLI separately through Atlassian's official setup flow.

Then from this folder:

```bash
npm install
forge deploy
forge install
```

## Environment Variables

Set the backend API URL when wiring the integration:

```text
GOVERNED_DELIVERY_API_URL=http://localhost:8787/api/analyze
```

For a real Forge deployment, this should point to a deployed backend service, not localhost.

## Production Notes

Before Marketplace or enterprise use, add:

- Atlassian authentication and permission hardening
- Backend authentication
- Tenant isolation
- Admin configuration screen
- Jira field mapping
- Parent-child issue creation rules by project type
- Rate limiting
- Security review
- Privacy policy
- Data retention policy
- Audit logging

## Safety Rule

Do not paste real PHI, PCI, credentials, secrets, or live client data into the demo.
