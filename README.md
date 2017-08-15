# turingsgang
An online judge for competitive programming.

## Setup

Rename the `config_template.py` file to `config.py` and enter all relevant config data.

Use a `virtualenv`.

Use with Nginx in production. See https://blog.marksteve.com/deploy-a-flask-application-inside-a-digitalocean-droplet/.

SSL is good. Read https://certbot.eff.org. Use the following cron job for automatic renewal: `43 1,13 * * * certbot renew --post-hook "service nginx reload"` (after running `crontab -e`).

Run the app with the command `gunicorn app:app`.

### Server

Nginx is used.

The nginx config file used is located at `/etc/nginx/conf.d/flask-app.conf`. To prevent nginx from loading the default configuration file, comment out the line `include /etc/nginx/sites-enabled/*;` in the file `/etc/nginx/nginx.conf`.


### Requirements

Run `pip install -r requirements.txt` to install all necessary libraries.

- Flask
- Gunicorn
- Redis
