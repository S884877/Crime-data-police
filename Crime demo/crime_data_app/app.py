from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import pandas as pd
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'fir_data.csv')
SECRET_KEY = os.environ.get('JWT_SECRET', 'super-secret-demo-key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Dummy users for demo purposes
USERS = {
    'admin': {'password': 'password123', 'role': 'admin'},
    'officer': {'password': 'beatpass', 'role': 'viewer'}
}

# Dummy coordinates for areas (for map markers)
AREA_COORDINATES = {
    'Downtown': (12.9716, 77.5946),
    'Northside': (12.9860, 77.6100),
    'Eastend': (12.9600, 77.6200),
    'Westpark': (12.9500, 77.5800)
}

app = FastAPI(title='Crime Data API')

# Allow CORS for local development / file:// access
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Mount static and templates directory so frontend files can be served
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')
app.mount('/templates', StaticFiles(directory=os.path.join(BASE_DIR, 'templates')), name='templates')

# Security dependency
bearer_scheme = HTTPBearer()


def load_data() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        cols = ['fir_id', 'date', 'time', 'area', 'crime_type', 'details']
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(CSV_PATH, parse_dates=['date'], dayfirst=True, dtype={'time': str})
    return df


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None or username not in USERS:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')


@app.get('/', response_class=JSONResponse)
def health_check():
    return {'status': 'running'}


@app.post('/login', response_class=JSONResponse)
def login(payload: Dict[str, str]):
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail='Username and password required')
    user = USERS.get(username)
    if not user or user.get('password') != password:
        raise HTTPException(status_code=401, detail='Invalid username or password')
    token = create_access_token({'sub': username, 'role': user.get('role')})
    return {'success': True, 'access_token': token, 'token_type': 'bearer'}


@app.get('/chain-snatching', response_class=JSONResponse)
def chain_snatching(
    area: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    token_data: dict = Depends(verify_token)
):
    """Return aggregated chain-snatching counts by area with optional filters and pagination."""
    df = load_data()
    if df.empty:
        return {'success': True, 'total': 0, 'results': [], 'limit': limit, 'offset': offset}

    # Normalize column names
    df.columns = [c.strip() for c in df.columns]

    # Filter for chain-snatching (case-insensitive match)
    if 'crime_type' in df.columns:
        mask = df['crime_type'].str.contains('chain', case=False, na=False)
        df = df[mask]
    else:
        return {'success': True, 'total': 0, 'results': [], 'limit': limit, 'offset': offset}

    # Filter by area
    if area:
        df = df[df['area'].str.lower() == area.lower()]

    # Filter by date range
    if start_date:
        try:
            sd = pd.to_datetime(start_date)
            df = df[df['date'] >= sd]
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid start_date format. Use YYYY-MM-DD')
    if end_date:
        try:
            ed = pd.to_datetime(end_date)
            df = df[df['date'] <= ed]
        except Exception:
            raise HTTPException(status_code=400, detail='Invalid end_date format. Use YYYY-MM-DD')

    # Filter by time range if column exists
    if start_time and 'time' in df.columns:
        df = df[df['time'].fillna('').str >= start_time]
    if end_time and 'time' in df.columns:
        df = df[df['time'].fillna('').str <= end_time]

    # Aggregate by area
    if 'area' in df.columns:
        grouped = df.groupby('area').size().reset_index(name='count').sort_values('count', ascending=False)
    else:
        grouped = pd.DataFrame(columns=['area', 'count'])

    total = int(grouped['count'].sum()) if not grouped.empty else 0

    # Apply pagination
    results_df = grouped.iloc[offset: offset + limit]

    results = []
    for _, row in results_df.iterrows():
        area_name = row['area']
        coords = AREA_COORDINATES.get(area_name, (0.0, 0.0))
        results.append({'area': area_name, 'count': int(row['count']), 'lat': coords[0], 'lng': coords[1]})

    return {'success': True, 'total': total, 'results': results, 'limit': limit, 'offset': offset}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={'success': False, 'detail': exc.detail})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('crime_data_app.app:app', host='0.0.0.0', port=8000, reload=True)
    from fastapi import FastAPI, HTTPException, Depends, Request, status
    from fastapi.responses import JSONResponse, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from jose import jwt, JWTError
    import pandas as pd
    import os
    from typing import Optional, Dict, Any
    from datetime import datetime, timedelta

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, 'fir_data.csv')
    SECRET_KEY = os.environ.get('JWT_SECRET', 'super-secret-demo-key')
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    # Dummy users for demo purposes
    USERS = {
        'admin': {'password': 'password123', 'role': 'admin'},
        'officer': {'password': 'beatpass', 'role': 'viewer'}
    }

    # Dummy coordinates for areas (for map markers)
    AREA_COORDINATES = {
        'Downtown': (12.9716, 77.5946),
        'Northside': (12.9860, 77.6100),
        'Eastend': (12.9600, 77.6200),
        'Westpark': (12.9500, 77.5800)
    }

    app = FastAPI(title='Crime Data API')

    # Allow CORS for local development / file:// access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )

    # Mount static and templates directory so frontend files can be served
    app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')
    templates_dir = os.path.join(BASE_DIR, 'templates')

    # Security dependency
    bearer_scheme = HTTPBearer()


    def load_data() -> pd.DataFrame:
        if not os.path.exists(CSV_PATH):
            # Create an empty dataframe with expected columns if missing
            cols = ['fir_id', 'date', 'time', 'area', 'crime_type', 'details']
            return pd.DataFrame(columns=cols)
        df = pd.read_csv(CSV_PATH, parse_dates=['date'], dayfirst=True, dtype={'time': str})
        return df


    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get('sub')
            if username is None or username not in USERS:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
            return payload
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')


    @app.get('/', response_class=JSONResponse)
    def health_check():
        return {'status': 'running'}


    @app.post('/login', response_class=JSONResponse)
    def login(payload: Dict[str, str]):
        username = payload.get('username')
        password = payload.get('password')
        if not username or not password:
            raise HTTPException(status_code=400, detail='Username and password required')
        user = USERS.get(username)
        if not user or user.get('password') != password:
            raise HTTPException(status_code=401, detail='Invalid username or password')
        token = create_access_token({'sub': username, 'role': user.get('role')})
        return {'success': True, 'access_token': token, 'token_type': 'bearer'}


    @app.get('/chain-snatching', response_class=JSONResponse)
    def chain_snatching(
        area: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        token_data: dict = Depends(verify_token)
    ):
        """Return aggregated chain-snatching counts by area with optional filters and pagination."""
        df = load_data()
        if df.empty:
            return {'success': True, 'total': 0, 'results': [], 'limit': limit, 'offset': offset}

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]

        # Filter for chain-snatching (case-insensitive match)
        if 'crime_type' in df.columns:
            mask = df['crime_type'].str.contains('chain', case=False, na=False)
            df = df[mask]
        else:
            return {'success': True, 'total': 0, 'results': [], 'limit': limit, 'offset': offset}

        # Filter by area
        if area:
            df = df[df['area'].str.lower() == area.lower()]

        # Filter by date range
        if start_date:
            try:
                sd = pd.to_datetime(start_date)
                df = df[df['date'] >= sd]
            except Exception:
                raise HTTPException(status_code=400, detail='Invalid start_date format. Use YYYY-MM-DD')
        if end_date:
            try:
                ed = pd.to_datetime(end_date)
                df = df[df['date'] <= ed]
            except Exception:
                raise HTTPException(status_code=400, detail='Invalid end_date format. Use YYYY-MM-DD')

        # Filter by time range if column exists
        if start_time and 'time' in df.columns:
            df = df[df['time'].fillna('').str >= start_time]
        if end_time and 'time' in df.columns:
            df = df[df['time'].fillna('').str <= end_time]

        # Aggregate by area
        if 'area' in df.columns:
            grouped = df.groupby('area').size().reset_index(name='count').sort_values('count', ascending=False)
        else:
            grouped = pd.DataFrame(columns=['area', 'count'])

        total = int(grouped['count'].sum()) if not grouped.empty else 0

        # Apply pagination
        results_df = grouped.iloc[offset: offset + limit]

        results = []
        for _, row in results_df.iterrows():
            area_name = row['area']
            coords = AREA_COORDINATES.get(area_name, (0.0, 0.0))
            results.append({'area': area_name, 'count': int(row['count']), 'lat': coords[0], 'lng': coords[1]})

        return {'success': True, 'total': total, 'results': results, 'limit': limit, 'offset': offset}


    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={'success': False, 'detail': exc.detail})


    if __name__ == '__main__':
        import uvicorn
        uvicorn.run('crime_data_app.app:app', host='0.0.0.0', port=8000, reload=True)