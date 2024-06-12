#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Ensure you are in the right directory
cd "$(dirname "$0")"

echo "Starting setup script..."

# Function to install dependencies for different OSes
install_dependencies() {
    OS=$(uname -s)
    ARCH=$(uname -m)

    if [ "$OS" == "Linux" ]; then
        if [ -f /etc/debian_version ]; then
            echo "Detected Ubuntu/Debian"
            sudo apt-get update
            sudo apt-get install -y wget cmake g++ libgles2-mesa-dev libglew-dev libglfw3-dev libglm-dev
        else
            echo "Unsupported Linux distribution"
            exit 1
        fi
    elif [ "$OS" == "Darwin" ]; then
        if [ "$ARCH" == "arm64" ]; then
            echo "Detected macOS ARM (M1/M2/...)"
            arch -arm64 brew install wget cmake llvm open-mpi libomp glm glew
        elif [ "$ARCH" == "x86_64" ]; then
            echo "Detected macOS x86_64 (Intel)"
            brew install wget cmake llvm open-mpi libomp glm glew
        else
            echo "Unsupported macOS architecture"
            exit 1
        fi
    else
        echo "Unsupported OS"
        exit 1
    fi
}

install_conda_environment() {
    if [ -d "infinigen" ]; then
        echo "Directory 'infinigen' already exists. Pulling latest changes..."
        cd infinigen
        git pull
    else
        echo "Cloning the 'infinigen' repository..."
        git clone https://github.com/RaccoonResearch/infinigen
        cd infinigen
    fi

    conda create --name infinigen python=3.10 -y
    source ~/miniconda3/etc/profile.d/conda.sh
    conda activate infinigen
    pip install -e .
    INFINIGEN_MINIMAL_INSTALL=True bash scripts/install/interactive_blender.sh
    mkdir -p outputs
}

install_dependencies
install_conda_environment