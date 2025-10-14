# IC Detection Deployment Guide

## 🚀 DEPLOYMENT OPTIONS

### Option 1: Render.com (Recommended - FREE)

1. **Push to GitHub:**
   ```bash
   cd "d:\SIH PS-162\ic-detection-yolo"
   git init
   git add .
   git commit -m "IC Detection Web App"
   git remote add origin YOUR_GITHUB_REPO
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to https://render.com
   - Sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your repository
   - Settings:
     - Name: `ic-detection`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1`
   - Click "Create Web Service"
   - ✅ Your app will be live at: `https://ic-detection.onrender.com`

### Option 2: Railway (FREE)

1. **Push to GitHub** (same as above)

2. **Deploy on Railway:**
   - Go to https://railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - ✅ Automatically deploys!

### Option 3: Heroku (FREE with verification)

1. **Install Heroku CLI**

2. **Deploy:**
   ```bash
   cd "d:\SIH PS-162\ic-detection-yolo"
   heroku login
   heroku create ic-detection-app
   git push heroku main
   heroku open
   ```

## 🧪 TEST LOCALLY FIRST

```bash
cd "d:\SIH PS-162\ic-detection-yolo"
pip install Flask gunicorn
python app.py
```

Open browser: http://localhost:5000

## 📋 FILES CREATED

- `app.py` - Flask web server
- `templates/index.html` - Beautiful UI
- `requirements.txt` - Updated with Flask
- `Procfile` - Deployment config
- `runtime.txt` - Python version

## 🎯 HOW IT WORKS

1. User uploads IC image
2. Server processes with YOLO + OpenCV
3. Returns detected ICs with bounding boxes
4. Shows confidence and count

## 🌐 WHAT YOU GET

- 📱 Mobile-friendly interface
- 🎨 Beautiful gradient design
- 📸 Drag & drop upload
- 🔍 Real-time detection
- 📊 Detection statistics
- ✅ Production-ready

## ⚠️ IMPORTANT NOTES

- **Vercel doesn't support Python** - Use Render/Railway instead
- **Free tier limits**: May be slow on first load (cold start)
- **Image size**: Keep under 5MB for fast processing
- **Model**: Uses YOLOv8n (lightweight, fast)

## 🔧 CUSTOM DOMAIN (Optional)

After deployment, you can add your own domain in platform settings.

## 💡 TROUBLESHOOTING

**Build fails?**
- Check requirements.txt
- Make sure all files are committed

**Slow detection?**
- Free tier has limited resources
- Upgrade plan for better performance

**Model not loading?**
- YOLOv8n will auto-download on first run
- May take 1-2 minutes on first request
