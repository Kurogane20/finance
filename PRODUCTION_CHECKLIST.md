# Production Deployment Checklist

Checklist wajib sebelum deploy ke production VPS. Pastikan semua item tercentang ✅.

## 🔐 Security Checklist

### Environment Variables
- [ ] Copy `.env.example` ke `.env`
- [ ] Generate SECRET_KEY baru: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Set SECRET_KEY di `.env` dengan hasil generate
- [ ] Set MYSQL_ROOT_PASSWORD dengan password yang kuat (min 16 karakter)
- [ ] Set MYSQL_PASSWORD dengan password yang kuat (min 16 karakter)
- [ ] Set DOMAIN dengan domain production Anda

### Frontend Configuration
- [ ] Update `frontend/.env.production`:
  ```
  VITE_API_URL=https://your-domain.com/api
  ```
- [ ] Rebuild frontend jika sudah di-build sebelumnya

### Default Accounts
- [ ] Setelah deploy, **SEGERA** ganti password semua akun demo:
  - admin@company.com
  - manager@company.com (jika ada)
  - akuntan@company.com
  - viewer@company.com

## 🌐 SSL/HTTPS Setup

- [ ] Pastikan domain sudah pointing ke IP VPS
- [ ] Jalankan Certbot untuk SSL:
  ```bash
  sudo certbot certonly --standalone -d finance.yourdomain.com
  ```
- [ ] Copy sertifikat ke folder nginx:
  ```bash
  mkdir -p nginx/ssl
  sudo cp /etc/letsencrypt/live/your-domain/fullchain.pem nginx/ssl/
  sudo cp /etc/letsencrypt/live/your-domain/privkey.pem nginx/ssl/
  ```

## 🐳 Docker Deployment

### Pre-deployment
- [ ] VPS sudah terinstall Docker & Docker Compose
- [ ] Port 80 dan 443 terbuka di firewall
- [ ] Minimal 1GB RAM tersedia

### Deployment Commands
```bash
# Clone/upload project
cd /opt
git clone <your-repo-url> finance
cd finance

# Setup environment
cp .env.example .env
nano .env  # Edit semua nilai

# Build dan jalankan
docker-compose up -d --build

# Cek status
docker-compose ps
docker-compose logs -f
```

## ✅ Post-Deployment Verification

- [ ] Akses https://your-domain.com - frontend loading
- [ ] Akses https://your-domain.com/api/docs - API docs accessible
- [ ] Login berhasil dengan akun demo
- [ ] Dashboard menampilkan data dengan benar
- [ ] Analytics insights muncul di dashboard
- [ ] Ganti semua password default!

## 🔥 Troubleshooting

### Container tidak jalan
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql
```

### Database connection error
```bash
# Tunggu MySQL fully ready
docker-compose restart backend
```

### SSL tidak bekerja
```bash
# Pastikan sertifikat sudah di-copy
ls -la nginx/ssl/
# Restart nginx
docker-compose restart frontend
```

---

## 📊 Monitoring (Recommended)

Untuk production, pertimbangkan menambahkan:
- [ ] Health check monitoring (UptimeRobot, etc)
- [ ] Log aggregation (optional)
- [ ] Backup database otomatis
- [ ] SSL auto-renewal cron job:
  ```bash
  0 0 1 * * certbot renew --quiet && docker-compose restart frontend
  ```
