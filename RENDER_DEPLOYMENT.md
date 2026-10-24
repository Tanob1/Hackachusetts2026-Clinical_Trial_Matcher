# 🚀 Render.com Deployment Instructions

## ✅ Pre-Deployment Checklist

All files are ready:
- ✅ render.yaml (Render configuration)
- ✅ requirements.txt (with gunicorn)
- ✅ app.py (production-ready)
- ✅ trials.db (3,131 trials, 0.69 MB)
- ✅ templates/ folder (6 HTML files)
- ✅ static/ folder (if exists)
- ✅ All Python files (database.py, matching.py, etc.)

---

## 📋 Step-by-Step Deployment

### Step 1: Commit All Changes
\\\ash
git add .
git commit -m "deploy: Configure for Render.com deployment"
git push origin main
\\\

### Step 2: Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub account
4. Authorize Render to access your repositories

### Step 3: Create New Web Service
1. Click "New +" button (top right)
2. Select "Web Service"
3. Connect your GitHub repository:
   - Repository: \Hackachusetts2026-Clinical_Trial_Matcher\
   - Or search for: \clinical-trial-matcher\
4. Click "Connect"

### Step 4: Configure Service
Render will auto-detect Python, but verify these settings:

**Basic Settings:**
- **Name:** \linkrtc\ (or your preferred name)
- **Region:** Oregon (US West) - closest to you
- **Branch:** \main\
- **Root Directory:** (leave blank)
- **Environment:** \Python 3\
- **Build Command:** \pip install -r requirements.txt\
- **Start Command:** \gunicorn app:app --bind 0.0.0.0:\ --workers 2 --timeout 60\

**Advanced Settings (Optional):**
- **Python Version:** \3.11.0\ (or leave default)
- **Health Check Path:** \/health\
- **Auto-Deploy:** \Yes\ (deploys on every git push)

### Step 5: Deploy!
1. Click "Create Web Service"
2. Wait for deployment (3-5 minutes)
3. Watch the build logs for any errors

### Step 6: Get Your URL
Once deployed, Render will give you a URL like:
\\\
https://linkrtc.onrender.com
\\\

---

## 🧪 Testing Your Deployment

### Test 1: Health Check
\\\ash
curl https://linkrtc.onrender.com/health
\\\

**Expected Response:**
\\\json
{
  "status": "healthy",
  "version": "1.0",
  "endpoints": { ... }
}
\\\

### Test 2: Patient Portal
Open in browser:
\\\
https://linkrtc.onrender.com/
\\\

**Test login:**
- Username: \sarah.chen\
- Password: \demo123\

### Test 3: Provider Portal
\\\
https://linkrtc.onrender.com/provider
\\\

**Test login:**
- Email: \dr.smith@hospital.org\
- Password: \provider123\

### Test 4: API Endpoint
\\\ash
curl https://linkrtc.onrender.com/api/demo/patients
\\\

**Expected:** JSON with 5 demo patients

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Sleeps after 15 minutes** of inactivity
- **First request takes ~30 seconds** to wake up
- **750 hours/month** of runtime (plenty for judging!)
- **Automatic HTTPS** included

### Wake-Up Solutions:
1. **For Judges:** Warn them first load may take 30s
2. **Keep Alive (Optional):** Ping every 10 minutes
   \\\ash
   # Create cron job or use UptimeRobot.com (free)
   curl https://linkrtc.onrender.com/health
   \\\

### Database Persistence:
- SQLite file is stored in the container
- **Survives restarts** ✅
- **Not lost on redeploy** ✅

---

## 🐛 Troubleshooting

### Build Failed?
**Check logs for:**
- Missing dependencies in requirements.txt
- Python version compatibility
- File path issues

**Fix:**
\\\ash
# Update requirements.txt
git add requirements.txt
git commit -m "fix: Update dependencies"
git push
# Render auto-redeploys
\\\

### 500 Internal Server Error?
**Check runtime logs:**
1. Go to Render dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for Python errors

**Common fixes:**
- Check DATABASE path is correct
- Verify all imports work
- Check file permissions

### App Doesn't Start?
**Verify Start Command:**
\\\ash
gunicorn app:app --bind 0.0.0.0:\ --workers 2 --timeout 60
\\\

**Test locally first:**
\\\ash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
# Open http://localhost:5000
\\\

---

## 🎯 What to Share with Judges

### Demo URLs:
\\\markdown
# LinkRTC - Live Demo on Render

## 🌐 Web Application
**URL:** https://linkrtc.onrender.com

⚠️ **Note:** First load may take 30 seconds (free tier wakes from sleep)

### Patient Portal
- **URL:** https://linkrtc.onrender.com/
- **Login:** sarah.chen / demo123
- **Features:** 
  - View matched trials
  - Edit medical conditions
  - Filter by distance and phase
  - Compare trials

### Provider Portal
- **URL:** https://linkrtc.onrender.com/provider
- **Login:** dr.smith@hospital.org / provider123
- **Features:**
  - Search patients
  - View patient matches
  - Generate QR code referrals

## 📊 API
- **Health:** https://linkrtc.onrender.com/health
- **Docs:** See API_DOCUMENTATION.md in repo

## 🎥 Video Demo
[Your video link]

## 📂 Source Code
**GitHub:** https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher
\\\

---

## 📊 Monitoring Your Demo

### Render Dashboard:
- View real-time logs
- See request metrics
- Monitor uptime
- Check resource usage

### During Judging:
1. **Keep dashboard open** to monitor
2. **Watch for errors** in logs
3. **Note judge access times** (30s wake-up warning)
4. **Verify everything works** before submission

---

## 🔧 Post-Deployment Tweaks

### Custom Domain (Optional):
1. Render Dashboard → Your Service
2. Settings → Custom Domain
3. Add: \linkrtc.yourdomain.com\
4. Update DNS (A record to Render IP)

### Environment Variables (If Needed):
1. Settings → Environment
2. Add variables:
   - \FLASK_ENV=production\
   - \SECRET_KEY=your-secret-key\ (for production)

### Increase Resources (If Free Tier Slow):
1. Upgrade to \/month plan
2. Get 512MB RAM + no sleep
3. Only if absolutely needed

---

## ✅ Deployment Complete!

Once deployed, you'll have:
- ✅ Live URL: https://linkrtc.onrender.com
- ✅ Automatic HTTPS
- ✅ Auto-deploy on git push
- ✅ Free tier (750 hours/month)
- ✅ Logs and monitoring
- ✅ Production-ready configuration

**Total Cost:** \ (Free tier)
**Deploy Time:** 3-5 minutes
**Availability:** 24/7 during judging

---

## 🎬 Quick Deploy Commands

\\\ash
# 1. Commit deployment files
git add .
git commit -m "deploy: Ready for Render.com"
git push origin main

# 2. Go to Render
# Visit: https://render.com
# New + → Web Service → Connect GitHub repo

# 3. Configure (use defaults + render.yaml)
# Click "Create Web Service"

# 4. Wait 3-5 minutes
# Get URL: https://linkrtc.onrender.com

# 5. Test it!
# Open in browser and verify everything works
\\\

---

## 📞 Support

**If deployment fails:**
1. Check Render build logs
2. Verify locally: \python app.py\
3. Check requirements.txt has all dependencies
4. Review troubleshooting section above

**Render Documentation:**
- https://render.com/docs/web-services
- https://render.com/docs/deploy-flask

---

## ✨ You're Ready!

Your LinkRTC project is **deployment-ready** for Render.com!

**Next Steps:**
1. ✅ Commit these changes
2. ✅ Push to GitHub
3. ✅ Deploy to Render (5 minutes)
4. ✅ Test your live demo
5. ✅ Share URL with judges

**Good luck with your hackathon! 🚀**

---

**Created:** January 30, 2025  
**Platform:** Render.com  
**Status:** Ready to Deploy  
**Cost:** FREE
