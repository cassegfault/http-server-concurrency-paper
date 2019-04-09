#!/bin/sh
pandoc --filter pandoc-citeproc docs/server.md -o http-server-concurrency.pdf
