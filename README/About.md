# About

A real-time GitHub webhook receiver built with Flask and MongoDB. This application:

- Captures GitHub events (Push, Pull Request, Merge) via webhooks
- Stores events in MongoDB
- Displays them on a live-updating dashboard
- Polls for new events every 15 seconds
