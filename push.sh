#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git config exists
if [[ -z $(git config --global user.name) ]] || [[ -z $(git config --global user.email) ]]; then
    echo -e "${GREEN}Setting up git configuration...${NC}"
    
    # Configure git
    echo -e "\n${GREEN}Enter your git username:${NC}"
    read git_username
    
    echo -e "\n${GREEN}Enter your git email:${NC}"
    read git_email
    
    git config --global user.name "$git_username"
    git config --global user.email "$git_email"
fi

# Initialize repository if not already initialized
if [ ! -d .git ]; then
    echo -e "\n${GREEN}Initializing git repository...${NC}"
    git init
    
    # Add remote repository
    echo -e "\n${GREEN}Adding remote repository...${NC}"
    git remote add origin https://github.com/prabhavjain2004/nfc.git
else
    # Update remote URL if repository exists
    git remote set-url origin https://github.com/prabhavjain2004/nfc.git
fi

# Check if there are any changes to commit
if [[ -z $(git status -s) ]]; then
    echo -e "${RED}No changes to commit${NC}"
    exit 0
fi

# Show current changes
echo -e "\n${GREEN}Current changes:${NC}"
git status -s

# Get commit message from user
echo -e "\n${GREEN}Enter commit message:${NC}"
read commit_message

if [[ -z "$commit_message" ]]; then
    echo -e "${RED}Commit message cannot be empty${NC}"
    exit 1
fi

# Add all changes
echo -e "\n${GREEN}Adding all changes...${NC}"
git add .

# Commit changes
echo -e "\n${GREEN}Committing changes...${NC}"
git commit -m "$commit_message"

# Push to remote
echo -e "\n${GREEN}Pushing to remote...${NC}"
git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Successfully pushed changes to remote!${NC}"
else
    echo -e "\n${RED}Failed to push changes. Please check your internet connection and try again${NC}"
fi
