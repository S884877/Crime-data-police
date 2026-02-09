# Crime Data Analysis API Documentation

## Overview

This is a beginner-friendly Flask REST API for analyzing crime datasets. The backend is designed to be simple, well-commented, and suitable for viva (oral examination) explanations.

**Base URL:** `http://127.0.0.1:5000`

---

## Features

✅ **File Upload** - Upload CSV files containing crime data  
✅ **CORS Enabled** - Frontend can communicate from any origin  
✅ **Multiple Analysis Endpoints** - Total crimes, by type, by year, by location  
✅ **Error Handling** - Comprehensive error messages with HTTP status codes  
✅ **Well-Documented Code** - Comments and docstrings for easy understanding  

---

## CSV Format

Expected columns in your CSV:
```
crime_type, location, year, severity
```

Example:
```csv
crime_type,location,year,severity
Theft,Downtown,2020,Low
Assault,Northside,2021,High
Burglary,East End,2022,Medium
```

---

## API Endpoints

### 1. Upload CSV File

**Endpoint:** `POST /api/upload`

**Description:** Upload a CSV file to the server for analysis.

**Request:**
```bash
curl -X POST -F "file=@crimes.csv" http://127.0.0.1:5000/api/upload
```

**Success Response (201):**
```json
{
  "message": "File uploaded successfully",
  "filename": "crimes.csv",
  "rows": 1000,
  "columns": ["crime_type", "location", "year", "severity"]
}
```

**Error Response (400):**
```json
{
  "error": "Invalid file type. Please upload a CSV file."
}
```

---

### 2. Get Total Crimes

**Endpoint:** `GET /api/crimes/total`

**Description:** Get the total number of crimes in the dataset.

**Parameters:**
- `file` (query, required): Filename in uploads folder

**Request:**
```bash
curl "http://127.0.0.1:5000/api/crimes/total?file=crimes.csv"
```

**Response (200):**
```json
{
  "total_crimes": 1000,
  "file": "crimes.csv"
}
```

---

### 3. Get Crimes by Type

**Endpoint:** `GET /api/crimes/by-type`

**Description:** Get crime counts grouped by crime type (e.g., Theft, Assault, etc.).

**Parameters:**
- `file` (query, required): Filename in uploads folder

**Request:**
```bash
curl "http://127.0.0.1:5000/api/crimes/by-type?file=crimes.csv"
```

**Response (200):**
```json
{
  "group_by": "crime_type",
  "total_crimes": 1000,
  "breakdown": [
    {"crime_type": "Theft", "count": 450},
    {"crime_type": "Assault", "count": 300},
    {"crime_type": "Burglary", "count": 150},
    {"crime_type": "Robbery", "count": 100}
  ]
}
```

---

### 4. Get Crimes by Year

**Endpoint:** `GET /api/crimes/by-year`

**Description:** Get crime counts grouped by year (time series data).

**Parameters:**
- `file` (query, required): Filename in uploads folder

**Request:**
```bash
curl "http://127.0.0.1:5000/api/crimes/by-year?file=crimes.csv"
```

**Response (200):**
```json
{
  "group_by": "year",
  "total_crimes": 1000,
  "breakdown": [
    {"year": 2020, "count": 250},
    {"year": 2021, "count": 300},
    {"year": 2022, "count": 450}
  ]
}
```

---

### 5. Get Crimes by Location

**Endpoint:** `GET /api/crimes/by-location`

**Description:** Get crime counts grouped by location (geographic analysis).

**Parameters:**
- `file` (query, required): Filename in uploads folder

**Request:**
```bash
curl "http://127.0.0.1:5000/api/crimes/by-location?file=crimes.csv"
```

**Response (200):**
```json
{
  "group_by": "location",
  "total_crimes": 1000,
  "breakdown": [
    {"location": "Downtown", "count": 400},
    {"location": "Northside", "count": 300},
    {"location": "East End", "count": 200},
    {"location": "Southside", "count": 100}
  ]
}
```

---

### 6. Legacy Summary Endpoint

**Endpoint:** `GET /api/summary`

**Description:** Get summary data grouped by any category (backward compatible with frontend).

**Parameters:**
- `file` (query, required): Filename in uploads folder
- `group_by` (query, optional): 'type', 'year', or 'location' (default: 'type')

**Request:**
```bash
curl "http://127.0.0.1:5000/api/summary?file=crimes.csv&group_by=type"
```

**Response (200):**
```json
[
  {"label": "Theft", "value": 450},
  {"label": "Assault", "value": 300},
  {"label": "Burglary", "value": 150},
  {"label": "Robbery", "value": 100}
]
```

---

## Error Handling

All endpoints return meaningful error messages with appropriate HTTP status codes:

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Data returned |
| 201 | Created | File uploaded |
| 400 | Bad Request | Missing required parameter |
| 404 | Not Found | File doesn't exist |
| 500 | Server Error | Unexpected error |

**Example Error Response:**
```json
{
  "error": "Missing 'file' query parameter"
}
```

---

## Code Structure

### Backend Files

1. **`app.py`** - Main Flask application
   - Route handlers for all endpoints
   - File upload handling
   - Error handling middleware
   - CORS configuration

2. **`utils/data_processing.py`** - Data analysis functions
   - `process_csv()` - Load and normalize CSV
   - `get_total_crimes()` - Count total crimes
   - `get_crimes_by_type()` - Group by crime type
   - `get_crimes_by_year()` - Group by year
   - `get_crimes_by_location()` - Group by location
   - `summarize_by()` - Legacy grouping function

3. **`requirements.txt`** - Python dependencies
   - Flask, pandas, flask-cors, etc.

---

## Testing with curl

**1. Upload a file:**
```bash
curl -X POST -F "file=@sample_crimes.csv" http://127.0.0.1:5000/api/upload
```

**2. Get total crimes:**
```bash
curl "http://127.0.0.1:5000/api/crimes/total?file=sample_crimes.csv"
```

**3. Get crimes by type:**
```bash
curl "http://127.0.0.1:5000/api/crimes/by-type?file=sample_crimes.csv"
```

**4. Get crimes by year:**
```bash
curl "http://127.0.0.1:5000/api/crimes/by-year?file=sample_crimes.csv"
```

**5. Get crimes by location:**
```bash
curl "http://127.0.0.1:5000/api/crimes/by-location?file=sample_crimes.csv"
```

---

## CORS Configuration

CORS (Cross-Origin Resource Sharing) is enabled globally, allowing the frontend to make requests from any origin.

In `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

This allows requests from:
- Different domains
- Different ports
- Different protocols (HTTP/HTTPS)

---

## Important Concepts for Viva

### 1. **REST API Principles**
- Uses HTTP methods: `GET` for retrieval, `POST` for submission
- Stateless: Each request is independent
- JSON format for request/response

### 2. **File Upload Handling**
- Uses `werkzeug.utils.secure_filename` to prevent security issues
- Validates file extensions before saving
- Stores files in `uploads/` directory

### 3. **Data Processing with pandas**
- Reads CSV with `pd.read_csv()`
- Normalizes column names (lowercase, remove spaces)
- Uses `value_counts()` for aggregation
- Handles missing values with `.fillna()`

### 4. **Flask Request Handling**
- `request.files` for file uploads
- `request.args.get()` for query parameters
- `request.json` for JSON body (not used here)

### 5. **HTTP Status Codes**
- 200: OK - Successful GET
- 201: Created - Successful POST
- 400: Bad Request - Invalid input
- 404: Not Found - Resource missing
- 500: Server Error - Unexpected failure

---

## Future Enhancements

- [ ] Add severity level analysis
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Authentication and authorization
- [ ] Date range filtering
- [ ] Data export (CSV, JSON)
- [ ] Advanced statistics (mean, median, std dev)
- [ ] Data visualization on backend

---

**Created:** February 2026  
**Status:** Production Ready
