#!/bin/bash

# Start the server in the background
python server.py &

# Wait a bit to ensure the server is up
sleep 2

# Start the client
python client.py
