# Security Policy

## Secrets handling
- Do not commit tokens, API keys, or credentials to the repository.
- Store secrets only in environment variables (GitHub Actions/Environments, deployment platform variables).
- Never add .env files to Git — keep them local.

## Local development
- Create a local .env file (not committed) with required variables, for example:
  - BOT_TOKEN=your_telegram_bot_token
- Export the variables before running locally, e.g. on Linux/macOS:
  ```bash
  export $(grep -v '^#' .env | xargs)
  ```
- Start the bot using the existing instructions in README.

## CI/CD and production
- Configure secrets in GitHub (Repository Settings → Secrets and variables → Actions) and in the deployment platform (e.g., Railway → Variables).
- Rotate any secret immediately if it is ever exposed.

## Preventing future leaks
- Ensure .env and similar files are ignored by Git.
- Enable GitHub Secret scanning and Push protection in Settings → Code security and analysis.
- Keep dependencies updated (Dependabot alerts).

## Reporting a security issue
If you discover a vulnerability or an exposed secret, do not open a public issue. Email the maintainer or use private contact channels to coordinate a fix and rotation.