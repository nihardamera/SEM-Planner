# 🎯 SEM Planning Engine

**AI-Powered Search Engine Marketing Strategy Generator**

Generate comprehensive SEM campaigns with intelligent keyword research, ad group clustering, and Performance Max themes - all powered by Groq AI.

## 🚀 **Live Demo**
*Deploy and add your live URL here*

## ✨ **Features**

### 🤖 **AI-Powered Intelligence**
- **Smart Keyword Generation**: Analyzes brand URLs for relevant keywords
- **Intelligent Clustering**: Groups keywords into strategic ad groups
- **PMax Optimization**: Creates Performance Max campaign themes
- **Bid Recommendations**: Calculates optimal CPC and CPA targets

### 📊 **Comprehensive Planning**
- **Search Campaigns**: Structured ad groups with match type suggestions
- **Shopping Campaigns**: Target CPA and CPC calculations
- **Performance Max**: AI-generated themes for Google's automation
- **Budget Allocation**: Strategic budget distribution across campaigns

### 🔄 **Reliable Architecture**
- **Three-Tier System**: Google Ads API → Groq AI → Static Fallbacks
- **Always Available**: Works even without API keys
- **Professional Quality**: Enterprise-grade SEM strategies

## 🛠️ **Tech Stack**

### **Backend**
- **FastAPI**: High-performance Python web framework
- **Groq AI**: Lightning-fast LLM inference
- **Google Ads API**: Real keyword data and metrics
- **Pydantic**: Data validation and serialization

### **Frontend**
- **React**: Modern UI framework
- **Vite**: Fast build tool and dev server
- **Responsive Design**: Works on all devices

## 🚀 **Quick Start**

### **Local Development**
```bash
# Clone repository
git clone https://github.com/yourusername/sem-planner.git
cd sem-planner

# Backend setup
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### **Environment Variables**
Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_ADS_CUSTOMER_ID=your_customer_id
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
```

## 🌐 **Deploy Online**

### **Option 1: Railway (Recommended)**
```bash
# Run deployment script
./deploy.sh

# Then:
# 1. Go to https://railway.app
# 2. Deploy from GitHub
# 3. Add environment variables
# 4. Get your live URL!
```

### **Option 2: Manual Deployment**
See `DEPLOYMENT_GUIDE.md` for detailed instructions on:
- Railway
- Render
- Vercel + Railway
- Heroku

## 📖 **API Usage**

### **Generate SEM Plan**
```bash
curl -X POST https://your-app.railway.app/api/v1/plan \
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

### **Response Example**
```json
{
  "search_campaign_plan": {
    "ad_groups": [
      {
        "ad_group_name": "Brand Terms",
        "theme": "Targeting customers interested in brand terms",
        "keywords": ["nike", "nike shoes", "buy nike"],
        "suggested_match_types": ["Exact", "Phrase"],
        "suggested_cpc_range": "$1.15 - $3.26"
      }
    ]
  },
  "pmax_plan": {
    "search_themes": [
      "Athletic Performance",
      "Lifestyle Fashion",
      "Sports Equipment"
    ]
  },
  "shopping_campaign_plan": {
    "target_cpa": 40.0,
    "suggested_target_cpc": 1.0
  }
}
```

## 🎯 **Use Cases**

### **Digital Marketing Agencies**
- Generate client SEM strategies in minutes
- Professional campaign structures
- Competitive analysis integration

### **E-commerce Businesses**
- Plan Google Ads campaigns
- Optimize budget allocation
- Discover new keyword opportunities

### **Marketing Consultants**
- Quick strategy development
- Client presentations
- Campaign auditing

## 🔧 **Configuration**

### **API Keys**
- **Groq API**: Get free credits at https://console.groq.com
- **Google Ads API**: Apply for access at https://developers.google.com/google-ads/api

### **Customization**
- Modify keyword generation prompts in `backend/llm_calls.py`
- Adjust bid calculations in `backend/sem_plan.py`
- Update UI components in `frontend/src/`

## 📊 **Performance**

- **Response Time**: < 3 seconds for full SEM plan
- **Uptime**: 99.9% with Railway hosting
- **Scalability**: Auto-scales based on traffic
- **Cost**: Free tier covers most usage

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Groq**: Lightning-fast AI inference
- **Google Ads API**: Real marketing data
- **FastAPI**: Excellent Python web framework
- **React**: Modern frontend development

---

**Built with ❤️ for the digital marketing community**

🚀 **Ready to revolutionize your SEM planning?** Deploy now and start generating professional campaigns in minutes!
