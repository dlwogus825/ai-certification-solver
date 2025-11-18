# Security Configuration Guide

## Environment Variables Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and set the following required variables:

### Required Environment Variables:

- **JWT_SECRET_KEY**: Secret key for JWT token generation
  - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  
- **DATABASE_URL**: MySQL database connection string
  - Format: `mysql+pymysql://username:password@host:port/database_name`
  
- **ANTHROPIC_API_KEY**: Your Anthropic API key for AI features

### Optional Environment Variables:

- **ADMIN_USERNAME**: Initial admin username (default: "admin")
- **ADMIN_PASSWORD**: Initial admin password (default: "change_this_password")
- **ADMIN_EMAIL**: Initial admin email (default: "admin@example.com")
- **CORS_ORIGINS**: Comma-separated list of allowed origins (default: "http://localhost,http://localhost:8080")
- **RATE_LIMIT_PER_MINUTE**: API rate limit per minute (default: 60)
- **RATE_LIMIT_PER_HOUR**: API rate limit per hour (default: 600)
- **MAX_FILE_SIZE_MB**: Maximum file upload size in MB (default: 10)

## Security Features Implemented:

1. **Environment Variables**: All sensitive data moved to environment variables
2. **File Upload Size Limit**: 10MB default limit configurable via environment variable
3. **Rate Limiting**: Implemented per-endpoint rate limiting
4. **CORS Configuration**: Configurable allowed origins
5. **JWT Secret Key**: Required in production, auto-generated only in development
6. **Admin Credentials**: Configurable via environment variables

## Running the Application:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Production Recommendations:

1. Always set strong JWT_SECRET_KEY in production
2. Use strong admin password
3. Configure CORS_ORIGINS to only allow your frontend domain
4. Adjust rate limits based on your expected traffic
5. Use HTTPS in production
6. Keep environment variables secure and never commit .env file