# Purging Secrets from Git History

This guide provides step-by-step instructions to permanently remove a secret (like your Telegram bot token) from the entire Git history of this repository.

## ⚠️ Important Warnings

- **History rewrite changes all commit SHAs** and requires force-pushing
- **All collaborators** will need to reclone or hard-reset their local repositories
- **Open PRs may need to be recreated** after the history rewrite
- If your repository was ever **public**, the secret may already be copied elsewhere
- This process **cannot be undone** easily - make sure you're ready

## Prerequisites

Before starting, ensure:
1. You have **admin access** to this repository
2. You have the **exact secret value** that needs to be purged
3. **No critical work** is in progress (coordinate with your team)
4. You're prepared for **all local clones to become outdated**

## Step-by-Step Instructions

### Step 1: Add the Secret to Repository Settings

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `SECRET_TO_PURGE`
5. Value: Paste the **exact secret value** you want to remove (e.g., your current bot token)
6. Click **Add secret**

### Step 2: Temporarily Disable Branch Protection (if enabled)

If your default branch has protection rules:

1. Go to **Settings** → **Branches**
2. Click **Edit** next to your default branch protection rule
3. **Temporarily disable** or **allow force pushes**
4. Click **Save changes**

⚠️ **Remember to re-enable protection after the purge!**

### Step 3: Run the Purge Workflow

1. Go to **Actions** tab in your repository
2. Select **Purge secret from Git history** workflow
3. Click **Run workflow**
4. Type `PURGE` in the confirmation field
5. Click **Run workflow**

### Step 4: Monitor the Workflow

- The workflow will take a few minutes to complete
- Monitor the logs to ensure success
- Look for the final "SUCCESS" message

### Step 5: Post-Purge Actions

After successful completion:

#### 5.1 Re-enable Branch Protection
1. Go back to **Settings** → **Branches**
2. Re-enable your protection rules
3. Save changes

#### 5.2 Notify Collaborators
Send this message to all collaborators:

```
🚨 URGENT: Git History Rewritten

The repository history has been rewritten to remove sensitive data.

ACTION REQUIRED:
1. Delete your local clone
2. Clone the repository again:
   git clone https://github.com/[YOUR-USERNAME]/hebrew-analytics-telegram-bot.git

OR if you want to keep your local work:
1. Backup uncommitted changes
2. Run: git fetch origin
3. Run: git reset --hard origin/main
4. Restore your uncommitted changes
```

#### 5.3 Check Open PRs
- Review all open Pull Requests
- Some may need to be closed and recreated
- The commit SHAs will have changed

#### 5.4 Verify Success
Run these commands locally to verify the secret is gone:
```bash
# This should return nothing
git log --all --full-history -S "YOUR_SECRET_HERE"

# This should also return nothing  
grep -r "YOUR_SECRET_HERE" .
```

## What the Workflow Does

1. **Validates** that `SECRET_TO_PURGE` is set
2. **Checks out** the full repository history
3. **Installs** `git-filter-repo` tool
4. **Rewrites history** replacing all occurrences of the secret with `REDACTED`
5. **Verifies** the secret is completely removed
6. **Force-pushes** all rewritten branches and tags back to GitHub

## After Purging

- The secret will show as `REDACTED` in all historical commits
- All commit SHAs will be different
- The repository structure and content remain the same
- Only the secret string has been replaced

## Rollback Considerations

There is **no easy rollback** for this operation. If something goes wrong:

1. **Stop the workflow** if it's still running
2. **Contact GitHub Support** if you need help
3. **Restore from a backup** if you have one (before running the purge)

## Security Notes

- The workflow **never echoes** the secret to logs (GitHub masks it automatically)
- The secret is **temporarily stored** in `/tmp/replace.txt` during the process
- The replacement file is **automatically cleaned up** after use

## Questions?

If you encounter issues:
1. Check the workflow logs for specific error messages
2. Ensure the `SECRET_TO_PURGE` secret is set correctly
3. Verify you have the necessary repository permissions
4. Consider reaching out to your team lead or repository admin

---

**Remember**: This is a **destructive operation** that rewrites Git history. Use with caution and ensure your team is coordinated before proceeding.