#!/usr/bin/env python
"""
List all registered routes in the Flask app
"""
from application import app

print("Registered Routes:\n")
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.rule:40} [{methods}]")
