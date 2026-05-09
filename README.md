# SAP BTP Python Hello World with XSUAA Authentication

A Python Flask application with SAP AppRouter demonstrating browser-based XSUAA authentication on SAP Business Technology Platform (BTP) Cloud Foundry.

## Architecture

```
Browser → AppRouter (Node.js) → Python Backend (Flask)
              ↓
         XSUAA Service
         (handles login)
```

The AppRouter handles user authentication automatically - when users access the app via browser, they are redirected to SAP login page and then forwarded to the Python backend with a valid JWT token.

## Project Structure

```
py-xsuaa-example/
├── approuter/
│   ├── package.json     # Node.js dependencies for AppRouter
│   └── xs-app.json      # AppRouter routing configuration
├── app/
│   ├── __init__.py
│   └── main.py          # Flask application with XSUAA integration
├── manifest.yml         # Cloud Foundry deployment manifest (2 apps)
├── xs-security.json     # XSUAA service configuration
├── requirements.txt     # Python dependencies
├── Procfile             # Process file for CF
├── runtime.txt          # Python runtime version
└── README.md            # This file
```

## Prerequisites

1. SAP BTP Account with Cloud Foundry environment
2. Cloud Foundry CLI installed
3. Python 3.11+ (for local development)
4. Node.js (for local AppRouter testing, optional)

## Deployment Steps

### 1. Login to Cloud Foundry

```bash
cf login -a https://api.cf.<region>.hana.ondemand.com
```

Replace `<region>` with your BTP region (e.g., `eu10`, `us10`, `ap10`).

### 2. Create XSUAA Service Instance

```bash
cf create-service xsuaa application py-xsuaa-service -c xs-security.json
```

### 3. Update manifest.yml (Required)

Edit `manifest.yml` and replace `us10` with your actual BTP region in the destinations URL:

```yaml
destinations: '[{"name":"py-backend","url":"https://py-xsuaa-backend.cfapps.<YOUR-REGION>.hana.ondemand.com","forwardAuthToken":true}]'
```

Common regions:
- EU10: `eu10.hana.ondemand.com`
- US10: `us10.hana.ondemand.com`
- AP10: `ap10.hana.ondemand.com`

### 4. Deploy the Applications

```bash
cf push
```

This deploys two applications:
- `py-xsuaa-approuter` - Node.js AppRouter (entry point)
- `py-xsuaa-backend` - Python Flask backend

### 5. Verify Deployment

```bash
cf apps
```

You should see both apps running.

## Accessing the Application

### Browser Access (Recommended)

Open in your browser:
```
https://py-xsuaa-approuter.cfapps.<region>.hana.ondemand.com/
```

You will be automatically redirected to SAP login. After authentication, you'll see your user information.

### API Endpoints

| Endpoint | Via AppRouter | Description |
|----------|--------------|-------------|
| `/` | Auto-login | Home page with user info |
| `/hello` | Auto-login | Protected hello endpoint |
| `/health` | No auth | Health check endpoint |

### Direct Backend Access (for testing)

The backend can also be accessed directly (without auto-login):
```
https://py-xsuaa-backend.cfapps.<region>.hana.ondemand.com/health
```

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app/main.py
```

The app will be available at `http://localhost:8080`

**Note:** Authentication won't work locally since XSUAA service is not bound. The `/health` endpoint will show `xsuaa_bound: false`.

## Configuration

### xs-security.json

XSUAA configuration for authentication only (no authorization scopes):

- `xsappname`: Unique identifier for your application
- `tenant-mode`: Set to `dedicated` for single-tenant deployment
- No scopes, roles, or role-collections defined

### manifest.yml

Deploys two applications:

**AppRouter (`py-xsuaa-approuter`):**
- Handles browser authentication
- Forwards requests to Python backend with JWT token
- Uses `nodejs_buildpack`

**Backend (`py-xsuaa-backend`):**
- Python Flask application
- Validates JWT tokens
- Uses `python_buildpack`

### approuter/xs-app.json

Routes all requests to the Python backend with XSUAA authentication:
- `authenticationType: xsuaa` - Requires login
- `forwardAuthToken: true` - Passes JWT to backend

## Troubleshooting

### XSUAA Service Not Bound

If `/health` shows `xsuaa_bound: false`:
1. Verify service exists: `cf services`
2. Check service binding: `cf env py-xsuaa-backend`
3. Restage if needed: `cf restage py-xsuaa-backend`

### AppRouter Not Redirecting to Login

1. Verify AppRouter is running: `cf apps`
2. Check AppRouter logs: `cf logs py-xsuaa-approuter --recent`
3. Ensure `xs-app.json` has `authenticationType: xsuaa`

### Backend Returns 401

1. Ensure you're accessing via AppRouter URL, not backend URL directly
2. Check backend logs: `cf logs py-xsuaa-backend --recent`
3. Verify destinations URL in manifest.yml matches backend URL

### Destination URL Mismatch

If AppRouter can't reach backend:
1. Run `cf apps` to get actual backend URL
2. Update `destinations` in manifest.yml with correct URL
3. Restage AppRouter: `cf restage py-xsuaa-approuter`

## License

MIT License
