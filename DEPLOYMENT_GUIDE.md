# 🚀 LinkRTC - Public Demo Deployment Guide

## Quick Start (5 Minutes to Live Demo)

### ⭐ Recommended: Railway.app (Easiest + Free)

#### Step 1: Prepare Your Project (Already Done! ✅)
- ✅ railway.json created
- ✅ Procfile created
- ✅ requirements-production.txt ready
- ✅ app.py updated for production

#### Step 2: Deploy to Railway
\\\ash
# Option A: Via Website (Easiest)
1. Go to https://railway.app
2. Sign up with GitHub (free)
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose: Hackachusetts2026-Clinical_Trial_Matcher
6. Railway auto-detects Flask ✅
7. Wait 2-3 minutes for build
8. Done! Get URL: linkrtc.up.railway.app

# Option B: Via CLI (Advanced)
npm install -g @railway/cli
railway login
railway init
railway up
\\\

#### Step 3: Access Your Live Demo
\\\
Patient Portal:  https://your-app.up.railway.app/
Provider Portal: https://your-app.up.railway.app/provider
API Health:      https://your-app.up.railway.app/health
\\\

#### Step 4: Share with Judges
\\\
🌐 Live Demo: https://your-app.up.railway.app

Demo Credentials:
Patient Login:
  - Username: sarah.chen
  - Password: demo123

Provider Login:
  - Email: dr.smith@hospital.org
  - Password: provider123

Features to Try:
✅ Patient Dashboard - View matched trials
✅ Edit Medical Conditions - Update profile
✅ Provider Portal - Search patients
✅ QR Code Generation - Send referrals
\\\

---

## Alternative Options

### Option 2: Render.com (100% Free)

#### Deploy:
\\\ash
1. Go to https://render.com
2. Sign in with GitHub
3. New → Web Service
4. Select your repository
5. Settings:
   - Name: linkrtc
   - Environment: Python 3
   - Build Command: pip install -r requirements-production.txt
   - Start Command: gunicorn app:app
6. Create Web Service
7. Wait 3-5 minutes
\\\

**URL:** https://linkrtc.onrender.com

**Note:** Free tier sleeps after 15 min inactivity. First load takes 30s.

---

### Option 3: Google Cloud Run (Most Professional)

#### Deploy:
\\\ash
# Install Google Cloud SDK first
# Then:

# 1. Create Dockerfile (already provided below)
# 2. Deploy
gcloud run deploy linkrtc \\
  --source . \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --memory 512Mi

# Get URL: https://linkrtc-xxx.run.app
\\\

---

## 📱 Mobile App Deployment

### Option A: Expo Web Build (Recommended)

\\\ash
# From mobile app directory
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"

# Build for web
npx expo export:web

# Deploy to Netlify
cd web-build
npx netlify-cli deploy --prod --dir .

# OR deploy to Vercel
vercel --prod
\\\

**Result:** Mobile app runs in browser!
**URL:** https://linkrtc.netlify.app

### Option B: Expo Published (For Expo Go App)

\\\ash
npx expo login
npx expo publish
\\\

**Share:** QR code or expo.dev/@yourname/linkrtc

---

## 🎯 Complete Demo Setup (All Components)

### Recommended Architecture:

\\\
┌─────────────────────────────────────────┐
│  Landing Page (GitHub Pages)            │
│  https://yourusername.github.io/linkrtc │
│  - Project overview                     │
│  - Links to all demos                   │
│  - Video demo                           │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼──────────┐   ┌───────▼──────────┐
│  Backend         │   │  Mobile App      │
│  (Railway)       │   │  (Netlify)       │
│  linkrtc.up      │   │  linkrtc.netlify │
│  .railway.app    │   │  .app            │
│                  │   │                  │
│  /           ←───┤   │  Web version of  │
│  /provider       │   │  mobile app      │
│  /api/*          │   │                  │
└──────────────────┘   └──────────────────┘
\\\

---

## 📋 Deployment Checklist

### Before Deploying:
- ✅ railway.json exists
- ✅ Procfile exists
- ✅ requirements-production.txt exists
- ✅ app.py updated for production
- ✅ SQLite database (trials.db) in repo
- ✅ All templates in templates/ folder
- ✅ Git repo up to date

### After Deploying:
- ✅ Test patient login (sarah.chen/demo123)
- ✅ Test provider login (dr.smith@hospital.org/provider123)
- ✅ Test trial search
- ✅ Test edit conditions
- ✅ Test QR code generation
- ✅ Check mobile responsiveness
- ✅ Verify HTTPS works

---

## 🐛 Troubleshooting

### Issue: "Module not found"
**Fix:** Make sure requirements-production.txt has all dependencies:
\\\
flask
pandas
werkzeug
qrcode[pil]
gunicorn
\\\

### Issue: "Database not found"
**Fix:** Make sure trials.db is committed to git:
\\\ash
git add trials.db
git commit -m "Add database for deployment"
git push
\\\

### Issue: "Port already in use"
**Fix:** Use PORT environment variable (already configured)

### Issue: "500 Internal Server Error"
**Fix:** Check logs:
\\\ash
# Railway: Click on deployment → View Logs
# Render: Click on service → Logs tab
# Google Cloud: gcloud logging read --limit 50
\\\

---

## 💰 Cost Comparison

| Platform | Free Tier | Cost for Judging | Best For |
|----------|-----------|------------------|----------|
| **Railway** | \ credit/month | FREE | Flask apps |
| **Render** | 750 hours/month | FREE | Simple demos |
| **Netlify** | 100GB bandwidth | FREE | Static + mobile |
| **Vercel** | Unlimited | FREE | Serverless |
| **Google Cloud** | \ credit | \-5 | Enterprise demo |
| **Expo** | Unlimited | FREE | Mobile app |

**Recommended for Hackathon:** Railway (backend) + Netlify (mobile)
**Total Cost:** \

---

## 🎬 Demo URLs to Share with Judges

\\\markdown
# LinkRTC - Live Demo

## 🌐 Web Application
**URL:** https://linkrtc.up.railway.app

### Patient Portal
- **Login:** https://linkrtc.up.railway.app/
- **Credentials:** 
  - Username: \sarah.chen\
  - Password: \demo123\
- **Try:** Edit conditions, view matches, filter trials

### Provider Portal  
- **Login:** https://linkrtc.up.railway.app/provider
- **Credentials:**
  - Email: \dr.smith@hospital.org\
  - Password: \provider123\
- **Try:** Search patients, generate QR referrals

## 📱 Mobile App
**URL:** https://linkrtc.netlify.app
- Try the mobile experience in your browser
- Works on phone, tablet, or desktop

## 📊 API Health Check
**URL:** https://linkrtc.up.railway.app/health

## 🎥 Video Demo
**URL:** [Your YouTube/Loom link]

## 📚 Documentation
**GitHub:** https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher
\\\

---

## 🚀 Deploy Now - Copy & Paste

\\\ash
# 1. Commit deployment files
git add railway.json Procfile requirements-production.txt app.py
git commit -m "deploy: Add Railway deployment configuration"
git push origin main

# 2. Deploy to Railway
# Go to https://railway.app
# New Project → Deploy from GitHub → Select your repo
# Done!

# 3. Get your URL
# Copy from Railway dashboard
# Share with judges!
\\\

---

## 📝 What to Include in Submission

### Links Section:
\\\
🌐 Live Demo: https://linkrtc.up.railway.app
📱 Mobile App: https://linkrtc.netlify.app  
📂 GitHub: https://github.com/Tanob1/Hackachusetts2026-Clinical_Trial_Matcher
🎥 Video: [Your demo video]
📖 Docs: See README.md
\\\

### Demo Credentials:
\\\
Patient:
  sarah.chen / demo123
  john.smith / demo123

Provider:
  dr.smith@hospital.org / provider123
\\\

### Test Instructions:
\\\
1. Login as patient Sarah Chen
2. Click "Edit Medical Conditions"  
3. Add "Diabetes" to conditions
4. Watch matches refresh with new trials
5. Login to provider portal as Dr. Smith
6. Search for "Sarah"
7. Click "Send Referral" on top trial
8. See generated QR code
\\\

---

## ⏱️ Timeline

| Task | Time | Status |
|------|------|--------|
| Create deployment files | 5 min | ✅ DONE |
| Push to GitHub | 1 min | Ready |
| Deploy to Railway | 3 min | Ready |
| Test deployment | 5 min | Ready |
| Deploy mobile to Netlify | 5 min | Ready |
| Create landing page | 10 min | Optional |
| **TOTAL** | **~30 min** | **READY** |

---

## 🎯 Judge Experience

When judges visit your demo:

1. **Landing page** shows overview
2. **Patient demo** - Can log in and try matching
3. **Provider demo** - Can generate QR codes
4. **Mobile demo** - Works in their browser
5. **GitHub** - Can review code
6. **Documentation** - Complete guides

**Impression:** Professional, complete, production-ready! 🏆

---

## 🔒 Security Notes

### For Demo:
- ✅ Use demo credentials (not real data)
- ✅ HTTPS enabled automatically
- ✅ Sessions secure with cookies
- ✅ No sensitive data exposed

### Not Production-Ready:
- ⚠️ SQLite (use PostgreSQL for production)
- ⚠️ Demo passwords (use real auth)
- ⚠️ No rate limiting
- ⚠️ No HIPAA compliance

**This is a demo for judging, not for real patients!**

---

## 📞 Support

If deployment fails:
1. Check Railway logs
2. Verify all files committed
3. Test locally first: \python app.py\
4. Check requirements-production.txt

---

## ✅ Ready to Deploy!

Your project is **deployment-ready**:
- ✅ Configuration files created
- ✅ Production settings configured
- ✅ Database included
- ✅ Git repo up to date

**Next Step:** Deploy to Railway (5 minutes)

**Result:** Live demo for judges! 🎉

---

**Updated:** January 30, 2025  
**Status:** Ready for Deployment  
**Est. Deploy Time:** 5-30 minutes  
**Cost:** \ (Free tier)
