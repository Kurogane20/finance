# Finance Dashboard - Deployment Guide

Panduan lengkap untuk deploy Finance Dashboard ke Ubuntu VPS.

## Prerequisites

- Ubuntu 20.04+ VPS dengan minimal 1GB RAM
- Domain name (opsional, untuk HTTPS)
- SSH access ke server

## Quick Deploy dengan Docker

### 1. Install Docker

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh

# Install Docker Compose
sudo apt install docker-compose -y

# Tambahkan user ke docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone dan Setup Project

```bash
# Clone repository (atau upload files)
cd /opt
sudo git clone https://github.com/yourusername/finance.git
cd finance

# Atau upload langsung via SCP:
# scp -r ./finance user@your-server-ip:/opt/
```

### 3. Konfigurasi Environment

```bash
# Copy dan edit environment file
cp .env.example .env
nano .env
```

Edit nilai-nilai berikut:
```
SECRET_KEY=your-random-32-character-secret-key
DOMAIN=finance.yourdomain.com
```

### 4. Update Frontend API URL

```bash
nano frontend/.env.production
```

Ubah ke:
```
VITE_API_URL=https://your-domain.com/api
```

### 5. Build dan Run

```bash
# Build dan jalankan containers
docker-compose up -d --build

# Lihat logs
docker-compose logs -f

# Cek status
docker-compose ps
```

Aplikasi akan berjalan di:
- Frontend: http://your-server-ip:80
- Backend API: http://your-server-ip:8000

---

## Deploy dengan HTTPS (Recommended)

### 1. Setup Nginx Reverse Proxy

```bash
# Install Nginx dan Certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# Stop nginx sementara
sudo systemctl stop nginx
```

### 2. Update docker-compose.yml

Uncomment bagian nginx di `docker-compose.yml` atau gunakan nginx host.

### 3. Dapatkan SSL Certificate

```bash
# Jalankan certbot
sudo certbot certonly --standalone -d finance.yourdomain.com

# Sertifikat akan tersimpan di:
# /etc/letsencrypt/live/finance.yourdomain.com/
```

### 4. Copy Sertifikat ke Project

```bash
mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/finance.yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/finance.yourdomain.com/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl
```

### 5. Restart Docker

```bash
docker-compose down
docker-compose up -d --build
```

---

## Deploy Manual (Tanpa Docker)

### 1. Install Dependencies

```bash
# Python dan Node.js
sudo apt install python3.11 python3.11-venv python3-pip nodejs npm nginx -y

# Install Node 20 (jika perlu)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

### 2. Setup Backend

```bash
cd /opt/finance/backend

# Buat virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan sekali untuk seed database
python -c "from seed_data import seed_database; seed_database()"
```

### 3. Buat Systemd Service untuk Backend

```bash
sudo nano /etc/systemd/system/finance-backend.service
```

Isi dengan:
```ini
[Unit]
Description=Finance Dashboard Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/finance/backend
Environment="PATH=/opt/finance/backend/venv/bin"
ExecStart=/opt/finance/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable dan start service
sudo systemctl enable finance-backend
sudo systemctl start finance-backend
sudo systemctl status finance-backend
```

### 4. Build Frontend

```bash
cd /opt/finance/frontend

# Install dependencies
npm install

# Build untuk production
npm run build

# Copy ke nginx folder
sudo cp -r dist/* /var/www/html/finance/
```

### 5. Konfigurasi Nginx

```bash
sudo nano /etc/nginx/sites-available/finance
```

```nginx
server {
    listen 80;
    server_name finance.yourdomain.com;

    root /var/www/html/finance;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/finance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup HTTPS dengan Certbot
sudo certbot --nginx -d finance.yourdomain.com
```

---

## Troubleshooting

### Cek Logs

```bash
# Docker logs
docker-compose logs backend
docker-compose logs frontend

# Systemd logs
sudo journalctl -u finance-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Database Reset

```bash
# Docker
docker-compose exec backend python -c "from seed_data import seed_database; seed_database()"

# Manual
cd /opt/finance/backend
source venv/bin/activate
python -c "from seed_data import seed_database; seed_database()"
```

### Restart Services

```bash
# Docker
docker-compose restart

# Manual
sudo systemctl restart finance-backend
sudo systemctl restart nginx
```

---

## Default Login

Setelah deploy, login dengan akun demo:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@company.com | admin123 |
| Manager | manager@company.com | manager123 |
| Akuntan | akuntan@company.com | akuntan123 |
| Staff | viewer@company.com | viewer123 |

⚠️ **PENTING**: Ganti password default setelah deploy ke production!
