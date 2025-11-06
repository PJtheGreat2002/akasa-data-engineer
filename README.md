# ✈️ Akasa Air Analytics Dashboard

A real-time interactive analytics dashboard for customer and order data analysis, built with Streamlit, Python, and MySQL.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [KPI Definitions](#kpi-definitions)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## ✨ Features

### 📊 Dashboard Features
- **Real-time Analytics**: Live data visualization and metrics
- **Interactive Charts**: Plotly-powered dynamic visualizations
- **Multi-page Interface**: Organized navigation with 4 main sections
- **Dual Processing**: Toggle between SQL and Pandas processing
- **Data Management**: Upload and process CSV/XML files
- **Export Functionality**: Download KPI results as CSV

### 🔍 Key Performance Indicators (KPIs)
1. **Repeat Customers**: Identify loyal customers with multiple orders
2. **Monthly Order Trends**: Track order patterns over time
3. **Regional Revenue**: Analyze revenue by geographic region
4. **Top Customers**: Monitor high-value customers

### 🛠️ Technical Features
- **Connection Pooling**: Efficient database connection management
- **Data Validation**: Comprehensive input validation and cleaning
- **Error Handling**: Robust error handling and logging
- **Caching**: Intelligent caching for improved performance
- **Responsive Design**: Works on desktop and mobile devices

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard (UI)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Overview   │  │  KPI Views  │  │  Data Processing    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend Services (Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  CSV Loader  │  │  XML Loader  │  │  Data Validator  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      KPI Engines (Table-based & Memory-based)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MySQL Database (Docker Container)               │
│           customers table  |  orders table                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

- **Python**: 3.8 or higher
- **Docker**: For MySQL container
- **Docker Compose**: For easy container management
- **Git**: For version control

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/akasa-data-pipeline.git
cd akasa-data-pipeline
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use any text editor
```

### 5. Start MySQL Container
```bash
# Start MySQL using Docker Compose
docker-compose up -d

# Verify container is running
docker-compose ps

# Check database tables
docker exec -it akasa_mysql mysql -uakasa_user -pakasa_pass akasa_db -e "SHOW TABLES;"
```

### 6. Load Sample Data (Optional)
```bash
# Generate sample data
python generate_sample_data.py

# Load data into database
python test_loaders.py
```

### 7. Run the Dashboard
```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

---

## 📖 Usage

### Starting the Application
```bash
# 1. Ensure MySQL is running
docker-compose up -d

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Run Streamlit
streamlit run app.py
```

### Uploading Data

1. Navigate to **Data Management** page
2. Click **Upload Files** tab
3. Upload `customers.csv` and `orders.xml`
4. Preview the data
5. Click **Process Data** tab
6. Select processing mode (replace/append)
7. Click **Process Both** button

### Viewing KPIs

1. Navigate to **KPI Analytics** page
2. Select processing method (SQL or Pandas)
3. Choose specific KPI or view all
4. Adjust parameters (time period, limits)
5. Export results as needed

### Monitoring System

1. Navigate to **System Logs** page
2. Filter by log level
3. Search for specific events
4. View error summary
5. Download logs if needed

---

## 📁 Project Structure
```
akasa-data-pipeline/
│
├── app.py                          # Main Streamlit application
├── docker-compose.yml              # Docker services configuration
├── init.sql                        # Database initialization
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
│
├── .streamlit/
│   └── config.toml                # Streamlit configuration
│
├── config/
│   ├── __init__.py
│   ├── config.py                  # Application configuration
│   └── db_config.py               # Database configuration
│
├── data/
│   ├── raw/                       # Input CSV/XML files
│   ├── processed/                 # Processed data cache
│   └── samples/                   # Sample data
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingestion/                 # Data ingestion modules
│   │   ├── __init__.py
│   │   ├── csv_loader.py         # CSV file loader
│   │   └── xml_loader.py         # XML file loader
│   │
│   ├── transformation/            # Data transformation
│   │   ├── __init__.py
│   │   ├── data_cleaner.py       # Data cleaning logic
│   │   └── data_validator.py     # Data validation
│   │
│   ├── database/                  # Database operations
│   │   ├── __init__.py
│   │   ├── db_manager.py         # Connection manager
│   │   └── db_operations.py      # CRUD operations
│   │
│   ├── kpis/                      # KPI calculation engines
│   │   ├── __init__.py
│   │   ├── base_kpi.py           # Base KPI class
│   │   ├── table_based_kpis.py   # SQL-based KPIs
│   │   └── memory_based_kpis.py  # Pandas-based KPIs
│   │
│   └── utils/                     # Utility modules
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       ├── cache_manager.py      # Caching utilities
│       └── validators.py         # Common validators
│
├── pages/                         # Streamlit pages
│   ├── 1_📊_Overview.py          # Overview dashboard
│   ├── 2_📈_KPI_Analytics.py     # KPI analytics
│   ├── 3_⚙️_Data_Management.py   # Data management
│   └── 4_📋_System_Logs.py       # System logs
│
├── tests/                         # Test files
│   ├── test_loaders.py
│   ├── test_kpis.py
│   └── test_setup.py
│
├── logs/                          # Application logs
│   └── app_YYYYMMDD.log
│
└── docs/                          # Documentation
    ├── DESIGN.md                 # System design
    ├── API.md                    # API documentation
    └── DEPLOYMENT.md             # Deployment guide
```

---

## 📊 KPI Definitions

### 1. Repeat Customers

**Definition**: Customers who have placed more than one order

**Calculation**:
```sql
SELECT customer_id, customer_name, COUNT(order_id) as order_count
FROM customers c JOIN orders o ON c.mobile_number = o.mobile_number
GROUP BY customer_id
HAVING COUNT(order_id) > 1
ORDER BY order_count DESC
```

**Business Value**: 
- Identify loyal customers for retention programs
- Target for loyalty rewards
- Understand customer lifetime value

---

### 2. Monthly Order Trends

**Definition**: Total orders and revenue aggregated by month

**Calculation**:
```sql
SELECT 
    DATE_FORMAT(order_date_time, '%Y-%m') as month_year,
    COUNT(order_id) as total_orders,
    SUM(total_amount) as total_revenue
FROM orders
GROUP BY month_year
ORDER BY month_year
```

**Business Value**:
- Demand forecasting
- Inventory planning
- Seasonal trend analysis

---

### 3. Regional Revenue

**Definition**: Revenue distribution by customer region

**Calculation**:
```sql
SELECT 
    c.region,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value
FROM customers c
LEFT JOIN orders o ON c.mobile_number = o.mobile_number
GROUP BY c.region
ORDER BY total_revenue DESC
```

**Business Value**:
- Geographic market analysis
- Regional marketing strategies
- Resource allocation

---

### 4. Top Customers (Last 30 Days)

**Definition**: Top 10 customers by spending in the last 30 days

**Calculation**:
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spend
FROM customers c
JOIN orders o ON c.mobile_number = o.mobile_number
WHERE o.order_date_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY c.customer_id
ORDER BY total_spend DESC
LIMIT 10
```

**Business Value**:
- VIP customer identification
- Personalized marketing
- High-value customer retention

---

## 🔧 Configuration

### Environment Variables
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=akasa_db
DB_USER=akasa_user
DB_PASSWORD=akasa_pass
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Application Settings
LOG_LEVEL=INFO
TIMEZONE=UTC

# Streamlit Settings
STREAMLIT_SERVER_PORT=8501
AUTO_REFRESH_INTERVAL=300

# Dashboard Settings
ENABLE_AUTO_REFRESH=true
CACHE_TTL=600
PAGE_TITLE=Akasa Air Analytics
PAGE_ICON=✈️
```

### Database Configuration

Edit `docker-compose.yml` to customize MySQL settings:
```yaml
environment:
  MYSQL_ROOT_PASSWORD: your_root_password
  MYSQL_DATABASE: your_database_name
  MYSQL_USER: your_username
  MYSQL_PASSWORD: your_password
```

---

## 🧪 Testing

### Run All Tests
```bash
# Test database connection
python test_setup.py

# Test data loaders
python test_loaders.py

# Test KPI engines
python test_kpis.py
```

### Unit Tests (Future)
```bash
pytest tests/ -v
```

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

**Symptoms**: 
```
Error: Can't connect to MySQL server
```

**Solutions**:
```bash
# Check if container is running
docker-compose ps

# Restart container
docker-compose restart mysql

# Check logs
docker-compose logs mysql
```

---

### Issue: Port Already in Use

**Symptoms**:
```
Error: Port 3306 is already allocated
```

**Solutions**:
```bash
# Find process using port 3306
lsof -i :3306  # macOS/Linux
netstat -ano | findstr :3306  # Windows

# Change port in docker-compose.yml
ports:
  - "3307:3306"

# Update .env
DB_PORT=3307
```

---

### Issue: Module Not Found

**Symptoms**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: Data Validation Errors

**Symptoms**:
```
Invalid mobile_number format
```

**Solutions**:
- Ensure mobile numbers are 8-15 digits
- Check CSV/XML file format
- Review validation rules in `src/utils/validators.py`

---

## 📈 Performance Optimization

### Database Indexing

The following indexes are created automatically:
- `customers.mobile_number`
- `customers.region`
- `orders.mobile_number`
- `orders.order_date_time`

### Caching Strategy

Streamlit caching is used for:
- KPI calculations (TTL: 10 minutes)
- Database queries (TTL: 10 minutes)
- Data loading (TTL: 10 minutes)

Clear cache: Settings → Clear Cache

---

## 🔐 Security

### Best Practices

1. **Environment Variables**: Never commit `.env` to version control
2. **Database Credentials**: Use strong passwords
3. **SQL Injection**: Use parameterized queries (already implemented)
4. **Access Control**: Implement authentication for production
5. **HTTPS**: Use SSL/TLS in production

### Production Checklist

- [ ] Change default passwords
- [ ] Enable SSL for MySQL
- [ ] Set up firewall rules
- [ ] Implement user authentication
- [ ] Enable HTTPS for Streamlit
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerts

---

## 🚢 Deployment

### Docker Deployment
```bash
# Build custom image (optional)
docker build -t akasa-dashboard .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Configure secrets
5. Deploy

#### AWS/GCP/Azure
Refer to `docs/DEPLOYMENT.md` for cloud-specific instructions

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Streamlit for the amazing framework
- Plotly for interactive visualizations
- MySQL for reliable data storage
- The Python community for excellent libraries

---

## 📧 Contact

**Project Link**: [https://github.com/yourusername/akasa-data-pipeline](https://github.com/yourusername/akasa-data-pipeline)

**Email**: your.email@example.com

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- [x] Basic dashboard with 4 KPIs
- [x] CSV/XML data loading
- [x] SQL and Pandas processing
- [x] Interactive charts
- [x] Data management interface

### Version 2.0 (Planned)
- [ ] User authentication
- [ ] Real-time data streaming
- [ ] Advanced analytics (ML predictions)
- [ ] Email notifications
- [ ] Scheduled reports
- [ ] API endpoints
- [ ] Mobile app

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

Made with ❤️ for Akasa Air