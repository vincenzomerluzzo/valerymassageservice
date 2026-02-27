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

## License
Specify the appropriate license here.
