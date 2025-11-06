# 🚀 Akasa Air Analytics - Setup Guide

Complete step-by-step guide to set up and run the Akasa Air Analytics Dashboard.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software

| Software | Version | Purpose | Download Link |
|----------|---------|---------|---------------|
| Python | 3.8 or higher | Backend runtime | [python.org](https://www.python.org/downloads/) |
| Docker | Latest | Database container | [docker.com](https://www.docker.com/get-started) |
| Docker Compose | Latest | Container orchestration | Included with Docker Desktop |
| Git | Latest | Version control | [git-scm.com](https://git-scm.com/) |

### Optional Tools

- **MySQL Workbench**: GUI for database management
- **VS Code**: Recommended code editor with Python extension
- **Postman**: For API testing (if API endpoints are added)

---

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 5 GB free space
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 10+ GB SSD
- **OS**: Latest stable versions
- **Network**: Stable internet for Docker image downloads

---

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/PJtheGreat2002/akasa-data-engineer.git

# Navigate to project directory
cd akasa-data-engineer

# Verify directory structure
ls -la
```

**Expected output:**
```
├── app.py
├── docker-compose.yml
├── init.sql
├── requirements.txt
├── README.md
├── .env.example
├── config/
├── data/
├── src/
├── pages/
└── ...
```

---

### Step 2: Create Virtual Environment

#### On macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show path to venv)
which python
```

#### On Windows:

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
```

**Verification:**
```bash
# Should show Python 3.8+
python --version

# Should show pip from venv
which pip  # macOS/Linux
where pip  # Windows
```

---

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages:**
```
streamlit==1.29.0
pandas==2.1.3
plotly==5.18.0
mysql-connector-python==8.2.0
SQLAlchemy==2.0.23
pymysql==1.1.0
python-dotenv==1.0.0
lxml==4.9.3
colorlog==6.8.0
pytz==2023.3
```

**Troubleshooting installation:**

```bash
# If installation fails, try one package at a time
pip install streamlit
pip install pandas
pip install plotly
# ... etc

# On macOS, if lxml fails:
brew install libxml2 libxslt
pip install lxml

# On Ubuntu, if MySQL connector fails:
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

---

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit the .env file
nano .env  # or use any text editor
```

**Required `.env` configuration:**

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=<database_name>
DB_USER=<username>
DB_PASSWORD=your_secure_password  # ⚠️ CHANGE THIS
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Application Settings
LOG_LEVEL=INFO
TIMEZONE=UTC

# Streamlit Settings
STREAMLIT_SERVER_PORT=8501
PAGE_TITLE=Akasa Air Analytics
PAGE_ICON=✈️
AUTO_REFRESH_INTERVAL=300
CACHE_TTL=600

# Feature Flags
ENABLE_AUTO_REFRESH=true
ENABLE_FILE_UPLOAD=true
ENABLE_MANUAL_REFRESH=true
ENABLE_EXPORT=true
```

⚠️ **Security Note:** 
- Never commit `.env` to version control
- Use strong passwords in production
- Keep `.env.example` as a template without sensitive data

---

## Configuration

### Database Configuration

Edit `docker-compose.yml` if you need custom database settings:

```yaml
environment:
  MYSQL_ROOT_PASSWORD: <your_root_password>  # Change this
  MYSQL_DATABASE: <database_name>
  MYSQL_USER: <username>
  MYSQL_PASSWORD: <your_secure_password> # Should match .env
```

**Important:** Ensure DB_PASSWORD in `.env` matches MYSQL_PASSWORD in `docker-compose.yml`

### Streamlit Configuration

Edit `.streamlit/config.toml` for UI customization:

```toml
[theme]
primaryColor = "#FF6B35"      # Akasa Air orange
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = true
enableCORS = false

[browser]
gatherUsageStats = false
```

---

## Database Setup

### Step 1: Start MySQL Container

```bash
# Start Docker services
docker-compose up -d

# Check if container is running
docker-compose ps
```

**Expected output:**
```
NAME          IMAGE       STATUS          PORTS
akasa_mysql   mysql:8.0   Up 10 seconds   0.0.0.0:3306->3306/tcp
```

### Step 2: Verify Database Initialization

```bash
# Check MySQL logs
docker-compose logs mysql

# Should see: "MySQL init process done. Ready for start up."
```

### Step 3: Connect and Verify Tables

```bash
# Connect to MySQL
docker exec -it akasa_mysql mysql -u<username> -p<password> <database_name>

# Inside MySQL prompt, run:
SHOW TABLES;
```

**Expected output:**
```
+------------------------+
| Tables_in_akasa_db     |
+------------------------+
| customer_order_summary |
| customers              |
| orders                 |
+------------------------+
```

```sql
-- Check table structure
DESCRIBE customers;
DESCRIBE orders;

-- Exit MySQL
EXIT;
```

### Step 4: Load Sample Data (Optional)

```bash
# Generate sample data
python generate_sample_data.py

# Load data into database
python test_loaders.py
```

**Expected output:**
```
============================================================
🚀 TESTING DATA LOADERS
============================================================

==================================================
Testing CSV Loader
==================================================
✅ CSV loaded successfully
   Records loaded: 20
   Duration: 0.15s

==================================================
Testing XML Loader
==================================================
✅ XML loaded successfully
   Records loaded: 50
   Duration: 0.12s

============================================================
✅ ALL LOADER TESTS PASSED!
============================================================
```

---

## Running the Application

### Quick Start

```bash
# 1. Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. Ensure Docker is running
docker-compose ps

# 3. Run Streamlit application
streamlit run app.py
```

**The application will automatically open in your browser at:**
```
http://localhost:8501
```

### Starting from Scratch

```bash
# Complete startup sequence

# 1. Navigate to project directory
cd akasa-data-pipeline

# 2. Start MySQL
docker-compose up -d

# 3. Wait for MySQL to initialize (first time only)
sleep 15

# 4. Activate Python environment
source venv/bin/activate

# 5. Run the application
streamlit run app.py
```

### Running in Development Mode

```bash
# Run with auto-reload on file changes
streamlit run app.py --server.runOnSave true

# Run on different port
streamlit run app.py --server.port 8502

# Run with debug logging
LOG_LEVEL=DEBUG streamlit run app.py
```

### Running in Production Mode

```bash
# Use production settings
streamlit run app.py --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection true \
  --browser.gatherUsageStats false
```
---
## Production Deployment

### Pre-deployment Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS for MySQL
- [ ] Set up firewall rules
- [ ] Configure environment variables for production
- [ ] Set up automated backups
- [ ] Configure monitoring and logging
- [ ] Test with production-like data volume
- [ ] Set up CI/CD pipeline
- [ ] Configure load balancing (if needed)
- [ ] Set up reverse proxy (nginx)

### Security Hardening

```bash
# 1. Use strong passwords
DB_PASSWORD=$(openssl rand -base64 32)

# 2. Restrict database access
# Edit docker-compose.yml
environment:
  MYSQL_ROOT_HOST: "localhost"  # Only local access

# 3. Enable SSL for MySQL
# Add to docker-compose.yml volumes:
- ./ssl:/etc/mysql/ssl

# 4. Use secrets management
# Install python-dotenv for production
pip install python-decouple

# 5. Set up monitoring
# Install sentry for error tracking
pip install sentry-sdk
```

### Docker Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: akasa_mysql_prod
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_prod_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
      - ./backups:/backups
    networks:
      - akasa_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 5
    command: 
      - --default-authentication-plugin=mysql_native_password
      - --max-connections=1000
      - --innodb-buffer-pool-size=2G

  streamlit:
    build: .
    container_name: akasa_app_prod
    restart: always
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=mysql
      - LOG_LEVEL=WARNING
    depends_on:
      mysql:
        condition: service_healthy
    networks:
      - akasa_network

volumes:
  mysql_prod_data:

networks:
  akasa_network:
    driver: bridge
```

### Backup Strategy

```bash
# Create backup script: backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Backup database
docker exec akasa_mysql mysqldump -uakasa_user -pakasa_pass akasa_db > \
  $BACKUP_DIR/akasa_db_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/akasa_db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: akasa_db_$DATE.sql.gz"

# Make executable
chmod +x backup.sh

# Add to crontab for daily backups at 2 AM
# 0 2 * * * /path/to/backup.sh
```

---

## Verification Tests

### Step 1: Test Database Connection

```bash
python test_setup.py
```

**Expected output:**
```
==================================================
🚀 AKASA AIR PIPELINE - SETUP TEST
==================================================

✅ Database: akasa_db
✅ Log Level: INFO
✅ Page Title: Akasa Air Analytics

✅ Database connection successful
✅ Table 'customers': 20 rows
✅ Table 'orders': 50 rows

==================================================
✅ ALL TESTS PASSED!
==================================================
```

### Step 2: Test Data Loaders

```bash
python test_loaders.py
```

### Step 3: Test KPI Engines

```bash
python test_kpis.py
```

### Step 4: Test Dashboard

1. Open browser to `http://localhost:8501`
2. Navigate through all pages:
   - Home (app)
   - Overview
   - KPI Analytics
   - Data Management
   - System Logs
3. Try uploading a file
4. View KPI calculations
5. Export data as CSV

---

## Getting Help

### Documentation

- **Setup Guide**: `SETUP.md` (this file)
- **Architecture**: `DESIGN.md`
- **Implementation**: `IMPLEMENTATION.md`
- **README**: `README.md`

### Support Channels

- **Issues**: Open an issue on GitHub
- **Email**: support@example.com
- **Slack**: #akasa-analytics (if available)

### Common Commands Reference

```bash
# Start everything
docker-compose up -d && streamlit run app.py

# Stop everything
docker-compose down

# Restart database
docker-compose restart mysql

# View logs
docker-compose logs -f mysql
tail -f logs/app_*.log

# Clean everything
docker-compose down -v
rm -rf data/processed/*
rm -rf logs/*

# Update dependencies
pip install --upgrade -r requirements.txt

# Run tests
python test_setup.py && python test_loaders.py && python test_kpis.py
```

---

## Success Criteria

✅ Docker container is running  
✅ Database tables are created  
✅ Sample data is loaded  
✅ Streamlit dashboard opens  
✅ All pages are accessible  
✅ KPIs display correctly  
✅ File upload works  
✅ No errors in logs  

---

## Next Steps

After successful setup:

1. **Customize Configuration**: Adjust settings in `.env`
2. **Load Real Data**: Upload your actual CSV/XML files
3. **Explore Dashboard**: Familiarize yourself with all features
4. **Read Documentation**: Review `DESIGN.md` and `IMPLEMENTATION.md`
5. **Start Development**: Make customizations as needed

---

**Setup complete! Your Akasa Air Analytics Dashboard is ready to use!** 🎉

For detailed architecture and implementation details, see:
- `DESIGN.md` - System architecture and design decisions
- `IMPLEMENTATION.md` - Code structure and implementation details