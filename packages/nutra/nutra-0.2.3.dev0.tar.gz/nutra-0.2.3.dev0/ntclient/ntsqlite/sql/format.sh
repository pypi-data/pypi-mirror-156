#!/bin/bash -ex

cd "$(dirname "$0")"

pg_format -s 2 -w 80 tables.sql -o tables.sql
pg_format -s 2 -w 80 functions.sql -o functions.sql