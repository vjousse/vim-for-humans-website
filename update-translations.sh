#!/bin/bash

pybabel extract -F babel.cfg -o messages.pot ./templates
pybabel update -i messages.pot -d translations
