#!/bin/bash

# Helper script to start all required services for the GitMesh application

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== GitMesh Development Environment Starter ===${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from template...${NC}"
    cp .env.template .env
    echo -e "${YELLOW}Please edit .env file with your actual credentials${NC}"
fi

# Check Python environment
echo -e "${BLUE}Checking Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${GREEN}Python virtual environment exists${NC}"
    source venv/bin/activate
fi

# Run GitHub configuration check
echo -e "\n${BLUE}Checking GitHub OAuth configuration...${NC}"
python scripts/check_github_config.py

echo -e "\n${BLUE}Starting Python backend server...${NC}"
echo -e "${YELLOW}Server will be available at http://localhost:3001${NC}\n"
uvicorn app:app --host 0.0.0.0 --port 3001 --reload
