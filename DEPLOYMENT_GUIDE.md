# 🚀 SEM Planning Engine - Deployment Guide

## 🎯 **Quick Deploy Options (Easiest to Hardest)**

### **Option 1: Railway (Recommended - Easiest)**
✅ **Free tier available**  
✅ **Automatic HTTPS**  
✅ **Zero configuration**  
✅ **Perfect for full-stack apps**

#### Steps:
1. **Create Railway Account**: Go to https://railway.app
2. **Connect GitHub**: Link your GitHub account
3. **Push Code**: Push your code to GitHub repository
4. **Deploy**: Click "Deploy from GitHub" on Railway
5. **Set Environment Variables**:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_ADS_CUSTOMER_ID=7891406099
   GOOGLE_ADS_DEVELOPER_TOKEN=your_token_here
   ```
6. **Get URL**: Railway provides a public URL automatically

---

### **Option 2: Render (Very Easy)**
✅ **Free tier available**  
✅ **Automatic deployments**  
✅ **Built-in database support**

#### Steps:
1. **Create Account**: Go to https://render.com
2. **Connect GitHub**: Link your repository
3. **Create Web Service**: Choose "Web Service"
4. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Add Environment Variables** (same as above)

---

### **Option 3: Vercel (Frontend) + Railway (Backend)**
✅ **Best performance**  
✅ **Separate scaling**  
✅ **Professional setup**

#### Frontend (Vercel):
1. Go to https://vercel.com
2. Import your GitHub repository
3. Set **Root Directory**: `frontend`
4. Deploy automatically

#### Backend (Railway):
1. Follow Railway steps above
2. Update frontend API calls to use Railway backend URL

---

### **Option 4: Heroku (Classic)**
⚠️ **No longer free**  
✅ **Very reliable**  
✅ **Professional grade**

#### Steps:
1. Install Heroku CLI
2. `heroku create your-sem-planner`
3. `git push heroku main`
4. Set environment variables with `heroku config:set`

---

## 🔧 **Pre-Deployment Checklist**

### ✅ **Files Ready**
- [x] `requirements.txt` - Python dependencies
- [x] `Procfile` - Deployment configuration
- [x] `railway.json` - Railway-specific config
- [x] `build.sh` - Build script
- [x] Environment variables configured

### ✅ **Environment Variables Needed**
```env
GROQ_API_KEY=gsk_your_actual_groq_key_here
GOOGLE_ADS_CUSTOMER_ID=7891406099
GOOGLE_ADS_DEVELOPER_TOKEN=your_token_here
```

### ✅ **CORS Configuration**
- [x] Updated to allow deployment domains
- [x] Supports Railway, Vercel, Netlify

---

## 🚀 **Recommended: Railway Deployment**

### **Why Railway?**
- **🆓 Free Tier**: $5/month in free credits
- **⚡ Fast**: Deploys in under 2 minutes
- **🔒 Secure**: Automatic HTTPS
- **📱 Mobile-Friendly**: Works on all devices
- **🔄 Auto-Deploy**: Updates automatically from GitHub

### **Step-by-Step Railway Deployment:**

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - SEM Planning Engine"
   git branch -M main
   git remote add origin https://github.com/yourusername/sem-planner.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to https://railway.app
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys!

3. **Add Environment Variables**:
   - Go to your project dashboard
   - Click "Variables" tab
   - Add your Groq API key and other variables

4. **Get Your URL**:
   - Railway provides a URL like: `https://your-app-name.railway.app`
   - Share this URL with anyone!

---

## 🎯 **After Deployment**

### **Test Your Live App**:
```bash
curl -X POST https://your-app-name.railway.app/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "brand_url": "https://www.nike.com",
    "competitor_url": "https://www.adidas.com",
    "service_locations": "USA",
    "search_ads_budget": 10000,
    "shopping_ads_budget": 15000,
    "pmax_ads_budget": 20000,
    "average_product_price": 120,
    "target_roas_percentage": 300
  }'
```

### **Share Your App**:
- ✅ **Backend API**: `https://your-app-name.railway.app`
- ✅ **Frontend**: Deploy separately or serve from backend
- ✅ **Demo Ready**: Professional SEM planning tool!

---

## 🔥 **Pro Tips**

### **Custom Domain** (Optional):
- Buy domain from Namecheap/GoDaddy
- Add CNAME record pointing to Railway
- Professional branding!

### **Monitoring**:
- Railway provides built-in logs
- Monitor API usage and performance
- Set up alerts for downtime

### **Scaling**:
- Railway auto-scales based on traffic
- Upgrade plan for higher limits
- Add database if needed

---

## 🎉 **You're Ready!**

Your SEM Planning Engine will be live at:
**`https://your-app-name.railway.app`**

Anyone can access it, create SEM plans, and get professional marketing strategies powered by AI! 🚀

**Estimated deployment time**: 5-10 minutes  
**Cost**: Free (with Railway's free tier)  
**Maintenance**: Zero - auto-updates from GitHub!
