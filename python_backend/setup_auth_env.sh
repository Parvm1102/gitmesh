#!/bin/bash

# Setup script for GitHub OAuth environment variables
# This script checks for required environment variables and sets them if missing

echo "🔵 Setting up GitHub OAuth environment variables..."

# Check for GitHub Client ID
if [ -z "$GITHUB_CLIENT_ID" ]; then
  echo "⚠️  GITHUB_CLIENT_ID not set"
  # Check if it's available in the JS backend environment
  if [ -f "../beetle_backend/.env" ]; then
    CLIENT_ID=$(grep "GITHUB_CLIENT_ID" ../beetle_backend/.env | cut -d '=' -f2)
    if [ ! -z "$CLIENT_ID" ]; then
      echo "✅ Found GITHUB_CLIENT_ID in JS backend .env, using it"
      export GITHUB_CLIENT_ID=$CLIENT_ID
    else
      echo "❌ Could not find GITHUB_CLIENT_ID in JS backend .env"
      echo "🔑 Please enter your GitHub Client ID:"
      read CLIENT_ID
      export GITHUB_CLIENT_ID=$CLIENT_ID
    fi
  else
    echo "❌ JS backend .env file not found"
    echo "🔑 Please enter your GitHub Client ID:"
    read CLIENT_ID
    export GITHUB_CLIENT_ID=$CLIENT_ID
  fi
else
  echo "✅ GITHUB_CLIENT_ID already set"
fi

# Check for GitHub Client Secret
if [ -z "$GITHUB_CLIENT_SECRET" ]; then
  echo "⚠️  GITHUB_CLIENT_SECRET not set"
  # Check if it's available in the JS backend environment
  if [ -f "../beetle_backend/.env" ]; then
    CLIENT_SECRET=$(grep "GITHUB_CLIENT_SECRET" ../beetle_backend/.env | cut -d '=' -f2)
    if [ ! -z "$CLIENT_SECRET" ]; then
      echo "✅ Found GITHUB_CLIENT_SECRET in JS backend .env, using it"
      export GITHUB_CLIENT_SECRET=$CLIENT_SECRET
    else
      echo "❌ Could not find GITHUB_CLIENT_SECRET in JS backend .env"
      echo "🔑 Please enter your GitHub Client Secret:"
      read CLIENT_SECRET
      export GITHUB_CLIENT_SECRET=$CLIENT_SECRET
    fi
  else
    echo "❌ JS backend .env file not found"
    echo "🔑 Please enter your GitHub Client Secret:"
    read CLIENT_SECRET
    export GITHUB_CLIENT_SECRET=$CLIENT_SECRET
  fi
else
  echo "✅ GITHUB_CLIENT_SECRET already set"
fi

# Check for GitHub Callback URL
if [ -z "$GITHUB_CALLBACK_URL" ]; then
  echo "⚠️  GITHUB_CALLBACK_URL not set"
  # Check if it's available in the JS backend environment
  if [ -f "../beetle_backend/.env" ]; then
    CALLBACK_URL=$(grep "GITHUB_CALLBACK_URL" ../beetle_backend/.env | cut -d '=' -f2)
    if [ ! -z "$CALLBACK_URL" ]; then
      echo "✅ Found GITHUB_CALLBACK_URL in JS backend .env, using it"
      export GITHUB_CALLBACK_URL=$CALLBACK_URL
    else
      echo "❌ Could not find GITHUB_CALLBACK_URL in JS backend .env"
      echo "🔗 Please enter your GitHub Callback URL (default: http://localhost:3001/api/v1/auth/github/callback):"
      read -p "URL: " CALLBACK_URL
      if [ -z "$CALLBACK_URL" ]; then
        CALLBACK_URL="http://localhost:3001/api/v1/auth/github/callback"
      fi
      export GITHUB_CALLBACK_URL=$CALLBACK_URL
    fi
  else
    echo "❌ JS backend .env file not found"
    echo "🔗 Please enter your GitHub Callback URL (default: http://localhost:3001/api/v1/auth/github/callback):"
    read -p "URL: " CALLBACK_URL
    if [ -z "$CALLBACK_URL" ]; then
      CALLBACK_URL="http://localhost:3001/api/v1/auth/github/callback"
    fi
    export GITHUB_CALLBACK_URL=$CALLBACK_URL
  fi
else
  echo "✅ GITHUB_CALLBACK_URL already set"
fi

# Check for JWT Secret
if [ -z "$JWT_SECRET" ]; then
  echo "⚠️  JWT_SECRET not set"
  # Check if it's available in the JS backend environment
  if [ -f "../beetle_backend/.env" ]; then
    JWT_SECRET=$(grep "JWT_SECRET" ../beetle_backend/.env | cut -d '=' -f2)
    if [ ! -z "$JWT_SECRET" ]; then
      echo "✅ Found JWT_SECRET in JS backend .env, using it"
      export JWT_SECRET=$JWT_SECRET
    else
      echo "❌ Could not find JWT_SECRET in JS backend .env"
      echo "🔑 Generating a random JWT secret"
      export JWT_SECRET=$(openssl rand -base64 32)
    fi
  else
    echo "❌ JS backend .env file not found"
    echo "🔑 Generating a random JWT secret"
    export JWT_SECRET=$(openssl rand -base64 32)
  fi
else
  echo "✅ JWT_SECRET already set"
fi

# Check for allowed origins
if [ -z "$ALLOWED_ORIGINS" ]; then
  echo "⚠️  ALLOWED_ORIGINS not set"
  # Default development origins
  export ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
  echo "✅ Set ALLOWED_ORIGINS to default: $ALLOWED_ORIGINS"
else
  echo "✅ ALLOWED_ORIGINS already set"
fi

# Save environment variables to .env file
echo "📝 Saving environment variables to .env file..."

# Create or update .env file
touch .env
grep -v "GITHUB_CLIENT_ID\|GITHUB_CLIENT_SECRET\|GITHUB_CALLBACK_URL\|JWT_SECRET\|ALLOWED_ORIGINS" .env > .env.tmp

echo "GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID" >> .env.tmp
echo "GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET" >> .env.tmp
echo "GITHUB_CALLBACK_URL=$GITHUB_CALLBACK_URL" >> .env.tmp
echo "JWT_SECRET=$JWT_SECRET" >> .env.tmp
echo "ALLOWED_ORIGINS=$ALLOWED_ORIGINS" >> .env.tmp

mv .env.tmp .env

echo "✅ Environment variables setup complete!"
echo ""
echo "ℹ️  To load these variables in your current shell, run:"
echo "source .env"
echo ""
echo "🚀 Ready to start the Python backend with GitHub OAuth support!"
