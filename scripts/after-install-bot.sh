#!/bin/bash
set -e

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable bot.service
systemctl restart bot.service
