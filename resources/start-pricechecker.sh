#!/bin/bash
echo "🚀 Starting PriceChecker..."
cd ~/projets/PriceChecker
if $?; then
    source .venv/bin/activate
    python run.py
else
    echo "PriceChecker directory not found. Please clone the repository first."
    exit 1
fi


