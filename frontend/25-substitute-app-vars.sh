#!/bin/sh
sed -i "s|http://localhost:8000/|${API_BASE}|g" /usr/share/nginx/html/assets/js/chat-app.js
