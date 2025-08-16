# Security Policy

## 🔐 Secrets and Sensitive Information

**NEVER commit secrets or sensitive information to this repository.** This includes:

- Telegram bot tokens (`BOT_TOKEN`)
- Google API credentials (`credentials.json`)
- Database passwords
- API keys
- Personal access tokens

## 🌍 Environment Variables

### For Local Development
Use environment variables to store sensitive information:

```bash
# Linux/Mac
export BOT_TOKEN="your_telegram_bot_token_here"

# Windows PowerShell
$env:BOT_TOKEN="your_telegram_bot_token_here"

# Windows Command Prompt
set BOT_TOKEN=your_telegram_bot_token_here
```

### For Production (Railway)
Set environment variables in your deployment platform:
- Railway: Project Settings → Variables
- Add `BOT_TOKEN` with your Telegram bot token value

## 📁 Local Configuration Files

### .env Files
- Create `.env` files for local development ONLY
- `.env` files MUST be included in `.gitignore` (already configured)
- Never commit `.env` files to version control

Example `.env` file structure:
```bash
# .env (local only - never commit!)
BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_CREDENTIALS_FILE=credentials.json
LOG_LEVEL=INFO
```

### Google Credentials
- Store `credentials.json` locally only
- This file is already ignored by `.gitignore`
- For production, use platform-specific secret management

## 🚨 Token Rotation and Incident Response

### If a Token is Leaked:

1. **Immediate Actions:**
   - Go to [@BotFather](https://t.me/BotFather) in Telegram
   - Send `/mybots` → select your bot → Bot Settings → Revoke Token
   - Generate a new token immediately

2. **Update Deployments:**
   - Update the `BOT_TOKEN` environment variable in Railway
   - Update your local development environment
   - Notify team members if applicable

3. **Repository Cleanup:**
   - If the token was committed to Git history, contact a repository administrator
   - Consider using `git filter-repo` for complete history cleanup (destructive operation)

### Invalidating Telegram Bot Tokens
- Tokens can be revoked through [@BotFather](https://t.me/BotFather)
- Revoked tokens become immediately inactive
- Always generate a new token after revocation

## 🛡️ GitHub Security Features

### Recommended Settings:
Enable these security features in repository settings:

1. **Secret Scanning** (Settings → Security → Code security and analysis)
   - Detects committed secrets automatically
   - Provides alerts for exposed tokens

2. **Push Protection** (Settings → Security → Code security and analysis)
   - Prevents pushing commits with detected secrets
   - Blocks commits before they reach the repository

3. **Dependabot Alerts** (Settings → Security → Code security and analysis)
   - Monitors dependencies for known vulnerabilities
   - Provides automated security updates

4. **Private Vulnerability Reporting** (Settings → Security)
   - Allows security researchers to report issues privately

## ✅ Pre-PR Security Checklist

Before opening a Pull Request, ensure:

- [ ] No hardcoded secrets in code or configuration files
- [ ] Environment variables are used for all sensitive data
- [ ] New dependencies are from trusted sources
- [ ] No `.env` files or `credentials.json` in the commit
- [ ] No temporary files with sensitive data
- [ ] Code follows the principle of least privilege
- [ ] Any new environment variables are documented

## 📋 Security Best Practices

### Code Security:
- Use environment variables for all configuration
- Implement input validation for user data
- Use secure file handling for uploads
- Implement proper error handling (don't expose internal details)

### Deployment Security:
- Use platform environment variables, not config files
- Keep dependencies updated
- Monitor logs for suspicious activity
- Implement rate limiting where appropriate

### Data Handling:
- Process user data securely
- Don't store sensitive user information unnecessarily  
- Implement proper cleanup of temporary files
- Use secure random generation for any tokens or IDs

## 🚨 Reporting Security Vulnerabilities

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Contact the repository maintainers privately
3. Provide details about the vulnerability
4. Allow time for the issue to be addressed before public disclosure

## 📚 Additional Resources

- [GitHub Security Documentation](https://docs.github.com/en/code-security)
- [Railway Environment Variables](https://docs.railway.app/reference/variables)
- [Telegram Bot Security Best Practices](https://core.telegram.org/bots/faq#security)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

---

**Remember**: Security is everyone's responsibility. When in doubt, ask for a security review before merging sensitive changes.