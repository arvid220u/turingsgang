# turingsgang
An online judge for competitive programming.

### Setup

Use a `virtualenv`.

Use with Nginx in production. See https://blog.marksteve.com/deploy-a-flask-application-inside-a-digitalocean-droplet/.

SSL is good. Read https://certbot.eff.org. Use the following cron job for automatic renewal: `43 1,13 * * * certbot renew --post-hook "service nginx reload"` (after running `crontab -e`).

Run the app with the command `gunicorn app:app`.

### Requirements

Run `pip install -r requirements.txt` to install all necessary libraries.

- Flask
- Gunicorn
