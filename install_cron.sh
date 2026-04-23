#!/bin/bash
# SRIE Core Cron Installer
# Adds a daily cron job to run the Orchestrator at 02:00 AM.

ORCHESTRATOR_PATH="/mnt/d/OpenClaw-Systems/xiaoyuan/projects/srie-core/orchestrator.py"
PYTHON_PATH="/usr/bin/python3"

echo "📅 Installing SRIE Cron Job..."

# Check if already installed
if crontab -l 2>/dev/null | grep -q "SRIE Orchestrator"; then
    echo "✅ SRIE Cron job already exists."
else
    # Add to crontab
    # 0 2 * * * = Daily at 2:00 AM
    (crontab -l 2>/dev/null; echo "0 2 * * * export AUTO_REFACTOR=true && $PYTHON_PATH $ORCHESTRATOR_PATH --force-auto >> /tmp/srie_orchestrator.log 2>&1 # SRIE Orchestrator") | crontab -
    echo "✅ SRIE Cron job installed. Runs daily at 02:00 AM."
fi

echo "📝 Current Crontab:"
crontab -l