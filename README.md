# Bytebase Docker Compose for Ogna Stack

A Docker Compose configuration for running Bytebase (database DevOps and CI/CD platform) as part of the Ogna stack.

## About Bytebase

Bytebase is an open-source database DevOps tool that helps teams manage database schema changes, version control database migrations, and implement database CI/CD workflows. It's ideal for collaborative database development and change management.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 2GB of available RAM
- Databases to manage (PostgreSQL, MySQL, MongoDB, etc.)

## Quick Start

1. Clone this repository:

```bash
git clone https://github.com/ognaapps/bytebase.git
cd bytebase
```

2. Create environment file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start Bytebase:

```bash
docker-compose up -d
```

4. Access Bytebase:
   - Open your browser and navigate to `http://localhost:8080`
   - Complete the initial setup wizard
   - Create your admin account
   - Add your database instances

## Configuration

### Default Settings

- **Bytebase Version**: Latest stable
- **Port**: 8080
- **Data Storage**: PostgreSQL (embedded) or external database
- **Data Persistence**: All data stored in Docker volumes

### Environment Variables

Edit your `.env` file with the following configurations:

```bash
# Basic Configuration
BYTEBASE_PORT=8080
BYTEBASE_HOST=0.0.0.0

# External URL (for webhooks and callbacks)
BYTEBASE_EXTERNAL_URL=http://localhost:8080

# Data Directory
BYTEBASE_DATA=/var/opt/bytebase

# Database Configuration (Bytebase's metadata database)
# Bytebase uses embedded PostgreSQL by default
# For production, consider external PostgreSQL

# PostgreSQL (Optional - External)
BYTEBASE_PG_URL=postgresql://user:password@postgres:5432/bytebase

# Authentication
# BYTEBASE_READONLY=false

# Debug Mode
# BYTEBASE_DEBUG=true

# Demo Mode (for testing)
# BYTEBASE_DEMO=true
```

## Accessing Bytebase

### Local Development

```
http://localhost:8080
```

### Production (with domain)

```
https://db.your-domain.com
```

## Initial Setup

### First Time Configuration

1. **Create Admin Account**

   - Navigate to `http://localhost:8080`
   - Set up administrator credentials
   - Configure workspace settings

2. **Add Database Instances**

   - Click "Instances" → "Add Instance"
   - Select database type
   - Enter connection details

3. **Example Database Connections** (Ogna Stack)

#### MongoDB

```
Name: Ogna MongoDB
Environment: Production
Type: MongoDB
Host: mongo (or host.docker.internal)
Port: 27017
Username: admin
Password: your_password
```

#### PostgreSQL

```
Name: Ogna PostgreSQL
Environment: Production
Type: PostgreSQL
Host: postgres
Port: 5432
Database: postgres
Username: postgres
Password: your_password
SSL: Optional
```

#### MySQL

```
Name: Ogna MySQL
Environment: Production
Type: MySQL
Host: mysql
Port: 3306
Username: root
Password: your_password
```

## Integration with Ogna Stack

Bytebase can manage database migrations across your entire Ogna stack:

### Version Control Integration

- Connect to GitHub/GitLab
- Store migrations in repository
- Review changes via pull requests

### CI/CD Integration

- Webhook support for automated deployments
- API for programmatic access
- Integration with n8n workflows

### Multi-Environment Support

- Development
- Staging
- Production
- Separate instances per environment

## Core Features

### Schema Migration

1. **Create Migration**

   - Navigate to "Projects" → Select project
   - Click "Alter Schema"
   - Write DDL statements:

   ```sql
   CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     email VARCHAR(255) UNIQUE NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

   - Create issue for approval

2. **Review & Approve**
   - Team members review changes
   - Approve or request modifications
   - Execute migration

### Schema Synchronization

- Compare schemas across environments
- Sync development to staging
- Generate diff reports

### Data Query

- Run read-only queries
- Export results to CSV
- Share query results with team

### Backup & Restore

- Schedule automatic backups
- Point-in-time recovery
- Backup verification

## Management

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f bytebase
```

### Restart Service

```bash
docker-compose restart bytebase
```

### Update Bytebase

```bash
docker-compose pull bytebase
docker-compose up -d
```

## Data Persistence

Data is persisted in Docker volumes:

- `bytebase_data`: Metadata, migration history, and configurations

### Backup Bytebase Data

```bash
# Stop Bytebase (optional, but recommended)
docker-compose stop bytebase

# Backup the data directory
docker run --rm \
  -v bytebase_bytebase_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/bytebase-backup-$(date +%Y%m%d).tar.gz -C /data .

# Start Bytebase
docker-compose start bytebase
```

### Restore Bytebase Data

```bash
# Stop Bytebase
docker-compose stop bytebase

# Restore
docker run --rm \
  -v bytebase_bytebase_data:/data \
  -v $(pwd)/backup:/backup \
  alpine sh -c "cd /data && tar xzf /backup/bytebase-backup-YYYYMMDD.tar.gz"

# Start Bytebase
docker-compose start bytebase
```

## Security Best Practices

⚠️ **Critical Security Steps**:

1. **Secure Admin Access**

   - Use strong passwords
   - Enable 2FA if available
   - Limit admin accounts

2. **Database Credentials**

   - Use least privilege principle
   - Create dedicated Bytebase users
   - Grant only necessary permissions

   ```sql
   -- PostgreSQL example
   CREATE USER bytebase WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE your_db TO bytebase;
   GRANT USAGE ON SCHEMA public TO bytebase;
   -- Grant specific permissions as needed
   ```

3. **Network Security**

   - Use Docker networks for isolation
   - Implement firewall rules
   - Use VPN for remote access

4. **SSL/TLS**

   - Enable SSL for database connections
   - Use HTTPS for web interface
   - Configure reverse proxy

5. **Audit Logging**

   - Enable audit logs
   - Monitor migration history
   - Track user activities

6. **Backup Strategy**
   - Regular automated backups
   - Test restore procedures
   - Store backups securely

## Reverse Proxy Setup (nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name db.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name db.your-domain.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Troubleshooting

### Bytebase Won't Start

- Check logs: `docker-compose logs bytebase`
- Verify port 8080 is available: `lsof -i :8080`
- Check disk space for data directory
- Verify Docker volume permissions

### Can't Connect to Database

- Verify database is running
- Check connection credentials
- Ensure database is accessible from Bytebase container
- Test connection:
  ```bash
  docker-compose exec bytebase ping postgres
  ```
- Check firewall rules
- Verify SSL settings if enabled

### Migration Failed

- Check database permissions
- Review SQL syntax
- Check database locks
- Review error logs in Bytebase UI
- Verify schema exists

### Slow Performance

- Check available system resources
- Optimize database queries
- Increase Docker memory limits
- Review database indexes

### Login Issues

- Clear browser cache
- Check `BYTEBASE_EXTERNAL_URL` setting
- Verify port mapping
- Check authentication configuration

### Data Loss After Restart

- Verify volumes are properly mounted
- Check volume permissions
- Ensure data directory is persistent

## Workflow Best Practices

### 1. GitOps Workflow

```
Developer → Creates PR with migration →
Review → Merge →
Bytebase auto-deploys →
Production update
```

### 2. Approval Process

- Require approvals for production changes
- Implement change windows
- Use rollback plans

### 3. Testing Strategy

- Test migrations in development first
- Use staging environment
- Verify backup before production

### 4. Naming Conventions

```
migrations/
  └── YYYYMMDD_HHMM_description.sql

Example:
  20240115_1430_add_users_table.sql
```

### 5. Documentation

- Document migration purpose
- Include rollback procedures
- Note dependencies

## API Usage

Bytebase provides REST API for automation:

```bash
# Get instances
curl -X GET http://localhost:8080/api/instance \
  -H "Authorization: Bearer YOUR_API_TOKEN"

# Create migration
curl -X POST http://localhost:8080/api/project/PROJECT_ID/issue \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Add users table",
    "type": "DDL",
    "statement": "CREATE TABLE users (id SERIAL PRIMARY KEY);"
  }'
```

## Integration Examples

### With n8n (Ogna Stack)

1. Create n8n workflow
2. Add webhook trigger
3. On merge to main branch
4. Trigger Bytebase migration via API

### With Git

1. Store migrations in repository
2. Configure webhook in Bytebase
3. Auto-sync on push

## Advanced Features

- **Schema Drift Detection**: Detect manual changes
- **Data Masking**: Protect sensitive data in non-prod
- **SQL Review**: Automated SQL linting
- **Batch Change**: Apply changes to multiple databases
- **Tenant Management**: Multi-tenant database management

## Database Support

Bytebase supports:

- PostgreSQL
- MySQL
- MongoDB
- Redis
- Oracle
- SQL Server
- MariaDB
- TiDB
- Snowflake
- ClickHouse
- And more...

## Resources

- [Bytebase Documentation](https://www.bytebase.com/docs/)
- [Migration Best Practices](https://www.bytebase.com/docs/change-database/migration-best-practices/)
- [API Reference](https://www.bytebase.com/docs/api/overview/)
- [Community Forum](https://github.com/bytebase/bytebase/discussions)

## License

[Specify your license]

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues and questions:

- Open an issue on [GitHub](https://github.com/ognaapps/bytebase/issues)
- Contact the Ogna team
- Check [Bytebase documentation](https://www.bytebase.com/docs/)

---

Made with ❤️ by the Ogna team
