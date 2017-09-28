#!/bin/bash
source judgevenv/bin/activate
killall gunicorn
gunicorn app:app
