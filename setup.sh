#!/usr/bin/env bash

# Enter the program folder
cd mixboard

# Create condo environment with the yml file 
conda env create -f environment.yml

# Activate the condo environment
Conda activate mixboard

# Install JS dependencies
npm install

# Install tmux 
brew install tmux


