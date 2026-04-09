# Valery Massage Service

This repository contains the source files for the Valery Massage Service website. It is a simple WordPress-based site with custom HTML and assets.

## Structure

- `index.html` – main landing page
- `wp-content/` – WordPress themes, plugins and uploads
- `img/` – moved image assets

## Deployment
The site can be deployed by copying the contents to a PHP-enabled web server.

### Automatic updates via cPanel

If your cPanel panel does not offer the built-in Git Version Control auto‑pull option, you can use one of the following approaches:

1. **GitHub webhook**
   - Put [`git-hook.php`](git-hook.php) in a web‑accessible location (e.g. `public_html/git-hook.php`).
   - Create a webhook on GitHub pointing to that URL (`https://yourdomain.example/git-hook.php`).
   - (Optional) set a secret in the webhook and copy it into the `$secret` variable inside `git-hook.php`.
   - Ensure the web user (typically `username` your cPanel account) has permission to run `git` operations in the repository directory.
   - When GitHub receives a push to `main`, it will POST to the script which pulls the latest changes and resets the working tree.

2. **Cron job poller**
   If webhooks aren’t possible, create a cron job in **Advanced → Cron Jobs** with a command such as:
   ```bash
   cd ~/public_html && git pull origin main
   ```
   Adjust the path and branch name as needed. Set the schedule to whatever frequency you prefer (every 5 minutes, hourly, etc.).

3. **Manual pull**
   You can always log in to cPanel’s terminal or use SSH and run `git pull` yourself whenever you need to update.

The `.cpanel.yml` file at the repository root defines additional deployment steps (e.g. rsync) and will run automatically when the above pulls occur.

### GitHub Actions FTP deploy (recommended)

This repository includes an automatic workflow at `.github/workflows/deploy-cpanel.yml`.
On each push to `main`, GitHub uploads files directly to cPanel via FTP.
No cPanel shell/SSH access is required.

1. In GitHub, open **Settings → Secrets and variables → Actions** and set these values (as **Secrets** or **Repository Variables**):
   - `CPANEL_FTP_SERVER` (example: `ftp.yourdomain.com`)
   - `CPANEL_FTP_USERNAME`
   - `CPANEL_FTP_PASSWORD`
   - `CPANEL_FTP_PORT` (optional, default is `21`)
   - `CPANEL_FTP_SERVER_DIR` (optional, default is `/public_html/`)
2. Push to `main` and check **Actions** tab for deploy logs.
3. Optional: run it manually via **Actions → Deploy To cPanel (FTP) → Run workflow**.

Safety notes:
- The workflow is configured to avoid touching typical server-managed files (`.htaccess`, `wp-*`, `cgi-bin`, `php.ini`).
- If your cPanel account hosts multiple apps in the same directory, prefer deploying to a dedicated subfolder.

### Make the repository private

To set the repository private:
1. Open GitHub repository page.
2. Go to **Settings → General → Danger Zone**.
3. Click **Change repository visibility** and select **Make private**.

Important:
- If your hosting uses "Git Version Control" inside cPanel, ensure cPanel can still authenticate to your private repo (deploy key/PAT).
- FTP deploy via GitHub Actions continues to work with private repositories.

## License
Specify the appropriate license here.
