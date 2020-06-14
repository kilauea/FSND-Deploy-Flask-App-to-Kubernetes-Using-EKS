#!/bin/bash

exec gunicorn -b :8080 main:APP
