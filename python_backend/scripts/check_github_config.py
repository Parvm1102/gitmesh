#!/usr/bin/env python3

"""
Script to check GitHub OAuth configuration.
This is helpful for verifying environment variables are set correctly.
"""

import os
import sys

def check_github_oauth_config():
    """Check GitHub OAuth configuration."""
    print("\n=== GitHub OAuth Configuration Check ===\n")
    
    # Required environment variables
    required_vars = [
        'GITHUB_CLIENT_ID', 
        'GITHUB_CLIENT_SECRET', 
        'GITHUB_CALLBACK_URL'
    ]
    
    # Optional environment variables
    optional_vars = [
        'JWT_SECRET',
        'FRONTEND_URL',
        'ALLOWED_ORIGINS',
        'NODE_ENV'
    ]
    
    missing_required = []
    
    # Check required vars
    print("Required Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print the full secret
            masked_value = value
            if var == 'GITHUB_CLIENT_SECRET' and len(value) > 8:
                masked_value = value[:4] + '...' + value[-4:]
            
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_required.append(var)
    
    # Check optional vars
    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            # Don't print the full secret
            masked_value = value
            if var == 'JWT_SECRET' and len(value) > 8:
                masked_value = value[:4] + '...' + value[-4:]
                
            print(f"  ✅ {var}: {masked_value}")
        else:
            print(f"  ⚠️  {var}: Not set")
    
    # Print summary
    print("\nSummary:")
    if missing_required:
        print(f"  ❌ Missing {len(missing_required)} required variables: {', '.join(missing_required)}")
        print("\nGitHub OAuth will not work correctly without these variables.")
        print("Set them in your environment before starting the application.")
        
        # Example .env file
        print("\nExample .env file content:")
        print("```")
        print("GITHUB_CLIENT_ID=your_github_client_id")
        print("GITHUB_CLIENT_SECRET=your_github_client_secret")
        print("GITHUB_CALLBACK_URL=http://localhost:3001/api/v1/auth/github/callback")
        print("JWT_SECRET=your_secure_jwt_secret_minimum_32_chars")
        print("FRONTEND_URL=http://localhost:3000")
        print("```")
        
        return False
    else:
        print("  ✅ All required variables are set.")
        return True

if __name__ == "__main__":
    success = check_github_oauth_config()
    sys.exit(0 if success else 1)
