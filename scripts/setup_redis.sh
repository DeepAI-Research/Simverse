#!/bin/bash

# Function to check if Redis is installed
check_redis_installed() {
    if command -v redis-server >/dev/null; then
        echo "Redis is already installed."
        return 0
    else
        echo "Redis is not installed."
        return 1
    fi
}

# Function to install Redis
install_redis() {
    echo "Installing Redis..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux installation (for Debian-based systems)
        sudo apt-get update
        sudo apt-get install redis-server -y
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS installation
        brew install redis
    else
        echo "Unsupported OS"
        exit 1
    fi
}

# Function to start Redis with default configuration
start_redis() {
    echo "Starting Redis..."
    redis-server --daemonize yes
    echo "Redis is running on port 6379 with default username and password."
}

# Main execution flow
check_redis_installed || install_redis
start_redis