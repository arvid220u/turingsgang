#!/bin/sh
killall gunicorn
gunicorn app:app
