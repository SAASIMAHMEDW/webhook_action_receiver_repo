# How to Run

## Prerequisites

- Python 3.13+ installed
- MongoDB (local or Atlas account)
- GitHub account (for webhook testing)
- ngrok account (for local webhook tunneling)

## Method 1: Local Development with UV (Recommended)

1. Clone and navigate:

   ```bash
   git clone <your-repo-url>
   cd webhook-repo
   ```

2. Install dependencies with UV:

   ```bash
   uv pip install -r requirements.txt
   ```

3. Create `.env` file:

   ```env
   MONGO_URI=mongodb://localhost:27017/github_webhooks
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

4. Run the application:

   ```bash
   python run.py
   ```

5. Access:
   - Dashboard: http://localhost:5000
   - API: http://localhost:5000/api/events

## Method 2: Local Development with Virtual Environment

1. Create virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate:

   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file (same as Method 1)

5. Run:
   ```bash
   python run.py
   ```

## Method 3: Docker (Single Container)

1. Build image:

   ```bash
   docker build -t webhook-app .
   ```

2. Run with Atlas:

   ```bash
   docker run -d -p 5000:5000 -e SECRET_KEY=super_secret -e MONGO_URI="xxx" --name webhook-app webhook-app
   ```

3. Or run with local MongoDB:
   ```bash
   docker run -d -p 5000:5000 -e MONGO_URI="mongodb://host.docker.internalgithub_webhooks" --name webhook-app webhook-app
   ```

## Method 4: Docker Compose (Recommended for Full Stack)

Create `.env.docker`:

```env
# MongoDB Configuration
MONGO_URI=xxx

# Flask Configuration
SECRET_KEY=super-secret

# Flask Environment
FLASK_ENV=production
FLASK_DEBUG=False
```

### Option A: MongoDB Atlas only

```bash
docker-compose --profile atlas up -d --build
```

App runs on: http://localhost:5000

### Option B: Local MongoDB + Backend

```bash
docker-compose --profile local up -d --build
```

- App runs on: http://localhost:5001
- MongoDB on: mongodb://localhost:27017

### Stop services:

```bash
docker-compose --profile atlas down
docker-compose --profile local down
```
