#!/bin/sh

export PYTHONPATH=$(pwd)/dafiti_geelbe_scraper
scrapy crawl "$*"