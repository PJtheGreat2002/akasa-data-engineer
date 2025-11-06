# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check
```bash
python --version  # Should be 3.8+
docker --version  # Should be installed
```

## 5-Minute Setup

### 1. Clone & Setup (1 min)
```bash
git clone <your-repo-url>
cd akasa-data-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Database (1 min)
```bash
docker-compose up -d
sleep 15  # Wait for MySQL to initialize
```

### 3. Generate Sample Data (1 min)
```bash
python generate_sample_data.py
python test_loaders.py
```

### 4. Run Dashboard (1 min)
```bash
streamlit run app.py
```

### 5. Explore! (1 min)
- Open browser to `http://localhost:8501`
- Navigate through pages
- View KPIs and charts

## Next Steps

- Upload your own data in **Data Management**
- Explore KPIs in **KPI Analytics**
- Check logs in **System Logs**
- Read full documentation in `README.md`

## Common Issues

**Port in use?**
```bash
# Change port in docker-compose.yml
ports: ["3307:3306"]
```

**Dependencies missing?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Need help?** Open an issue on GitHub!