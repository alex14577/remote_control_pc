#!/bin/bash
set -e

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable agent.service
systemctl restart agent.service
