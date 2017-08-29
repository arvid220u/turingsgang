# turingsgang
An online judge for competitive programming.

## Setup

Rename the `config_template.py` file to `config.py` and enter all relevant config data.

Use a `virtualenv`. (Install with `pip3 install virtualenv`. Create a `virtualenv` in the project directory using `virtualenv judgevenv`. Activate using `source judgevenv/bin/activate`.)

Use with Nginx in production. See https://blog.marksteve.com/deploy-a-flask-application-inside-a-digitalocean-droplet/. Append the following to `/etc/nginx/conf.d/flask-app.conf` if you want to redirect www to non-www (which is highly advisable): 
```
server {
    server_name www.matteklubbenfibonacci.se;
    return 301 https://matteklubbenfibonacci.se$request_uri;
}
```

SSL is good. Read https://certbot.eff.org. Use the following cron job for automatic renewal: `43 1,13 * * * certbot renew --post-hook "service nginx reload"` (after running `crontab -e`).

Run the app with the command `gunicorn app:app`.


### Database

Set up the database by running `sqlite3 app.db < schema.sql`.

The database should be backed up daily. Add `22 4 * * * sqlite3 /path/to/app.db ".backup /path/to/app.db.bak"` to `crontab -e`.

### Server

Nginx is used.

The nginx config file used is located at `/etc/nginx/conf.d/flask-app.conf`. To prevent nginx from loading the default configuration file, comment out the line `include /etc/nginx/sites-enabled/*;` in the file `/etc/nginx/nginx.conf`.


### Redis

Redis is used for the judging queue.

Use the `screen` command tool to manage Redis. We need two screens: (1) redis, and (2) redisdaemon. (1) runs the command `redis-server`, and (2) runs the command `./redisdaemon.py`.

### Requirements

Run `pip install -r requirements.txt` to install all necessary libraries.

- Flask
- Gunicorn
- Redis
