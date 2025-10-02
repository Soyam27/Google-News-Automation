#!/bin/bash

# Install Chromium & ChromeDriver
apt update
apt install -y chromium chromium-driver

# Run Python script
python3 main.py
