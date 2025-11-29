# 🚀 Azure Deployment Guide - Step by Step

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Azure account (free tier works: https://azure.microsoft.com/free/)
- [ ] Docker Desktop installed (https://www.docker.com/products/docker-desktop/)
- [ ] Azure CLI installed (https://aka.ms/installazurecliwindows)
- [ ] Git installed (optional, for version control)
- [ ] Vercel account (free: https://vercel.com/signup)

---

## Part 1: Test Locally First

### Step 1: Test the API Server Locally

```powershell
# Navigate to your project
cd c:\Users\d3vsh\Downloads\backupMH

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py
```

The server should start at `http://localhost:8000`. Open your browser and visit:
- `http://localhost:8000` - Health check
- `http://localhost:8000/docs` - Interactive API documentation

### Step 2: Test the Frontend Locally

Open a new terminal:

```powershell
cd c:\Users\d3vsh\Downloads\backupMH\frontend

# Start a simple HTTP server
python -m http.server 3000
```

Visit `http://localhost:3000` in your browser. The frontend should load and connect to your local backend.

**Test both voice and text modes!**

---

## Part 2: Deploy Backend to Azure

### Step 1: Install and Login to Azure CLI

```powershell
# Install Azure CLI (if not already installed)
winget install Microsoft.AzureCLI

# Login to Azure
az login
```

A browser window will open for authentication.

### Step 2: Create Azure Resources

```powershell
# Set variables (customize these)
$RESOURCE_GROUP="insurance-agent-rg"
$LOCATION="eastus"
$ACR_NAME="insuranceagentacr"  # Must be globally unique, lowercase only
$APP_NAME="insurance-voice-agent"  # Must be globally unique

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Enable admin access
az acr update -n $ACR_NAME --admin-enabled true

# Get ACR credentials
az acr credential show --name $ACR_NAME
```

**Save the username and password from the last command!**

### Step 3: Build and Push Docker Image

```powershell
# Navigate to project directory
cd c:\Users\d3vsh\Downloads\backupMH

# Login to ACR
az acr login --name $ACR_NAME

# Build Docker image
docker build -t insurance-voice-agent:v1 .

# Tag for ACR
docker tag insurance-voice-agent:v1 ${ACR_NAME}.azurecr.io/insurance-voice-agent:v1

# Push to ACR
docker push ${ACR_NAME}.azurecr.io/insurance-voice-agent:v1
```

### Step 4: Deploy to Azure App Service

```powershell
# Create App Service Plan
az appservice plan create `
  --name insurance-agent-plan `
  --resource-group $RESOURCE_GROUP `
  --is-linux `
  --sku B1

# Create Web App
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan insurance-agent-plan `
  --name $APP_NAME `
  --deployment-container-image-name ${ACR_NAME}.azurecr.io/insurance-voice-agent:v1

# Configure ACR credentials
az webapp config container set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --docker-custom-image-name ${ACR_NAME}.azurecr.io/insurance-voice-agent:v1 `
  --docker-registry-server-url https://${ACR_NAME}.azurecr.io `
  --docker-registry-server-user $ACR_NAME `
  --docker-registry-server-password <PASSWORD_FROM_STEP_2>

# Set environment variables
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings WEBSITES_PORT=8000

# Enable CORS (important for frontend)
az webapp cors add `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --allowed-origins '*'

# Get your app URL
az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query defaultHostName -o tsv
```

**Your backend is now live!** The URL will be something like: `https://insurance-voice-agent.azurewebsites.net`

### Step 5: Verify Backend Deployment

Visit these URLs in your browser:
- `https://<your-app-name>.azurewebsites.net/` - Health check
- `https://<your-app-name>.azurewebsites.net/health` - Detailed health
- `https://<your-app-name>.azurewebsites.net/docs` - API documentation

---

## Part 3: Deploy Frontend to Vercel

### Step 1: Update API URL in Frontend

Edit `frontend/app.js` and change line 2:

```javascript
const API_URL = 'https://<your-app-name>.azurewebsites.net';
```

Replace `<your-app-name>` with your actual Azure app name.

### Step 2: Deploy to Vercel

```powershell
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend directory
cd c:\Users\d3vsh\Downloads\backupMH\frontend

# Deploy
vercel
```

Follow the prompts:
1. "Set up and deploy?" → **Yes**
2. "Which scope?" → Choose your account
3. "Link to existing project?" → **No**
4. "What's your project's name?" → **insurance-ai-assistant**
5. "In which directory is your code located?" → **./** (press Enter)
6. "Want to override settings?" → **No**

Vercel will deploy and give you a URL like: `https://insurance-ai-assistant.vercel.app`

### Step 3: Test Your Deployed Application

1. Visit your Vercel URL
2. Check connection status (should show "Connected")
3. Test text mode first
4. Then test voice mode (allow microphone access)

---

## Part 4: Optional - Custom Domain

### For Vercel (Frontend):

1. Go to your project dashboard on Vercel
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### For Azure (Backend):

```powershell
az webapp config hostname add `
  --webapp-name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --hostname yourdomain.com
```

---

## 🔧 Troubleshooting

### Backend Issues

**Container won't start:**
```powershell
# View logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
```

**Database not found:**
- Check if `chroma_insurance_db` was included in Docker image
- Run: `docker build -t test .` locally and verify

**API key issues:**
- Verify `apikeys.env` is in the Docker image
- Check environment variables are set correctly

### Frontend Issues

**Cannot connect to backend:**
- Verify API_URL in `app.js` is correct
- Check CORS is enabled on Azure
- Open browser console (F12) to see errors

**Microphone not working:**
- Ensure you're using HTTPS (required for microphone access)
- Check browser permissions
- Try different browser (Chrome/Edge recommended)

---

## 📊 Monitoring & Costs

### View Logs

```powershell
# Stream logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

# Download logs
az webapp log download --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### Estimated Costs

- **Azure App Service B1:** ~$13/month
- **Azure Container Registry Basic:** ~$5/month
- **Vercel Free Tier:** $0/month
- **Total:** ~$18/month

### Free Tier Alternative

Use **Azure Container Instances** instead (pay per second):

```powershell
az container create `
  --resource-group $RESOURCE_GROUP `
  --name insurance-agent-api `
  --image ${ACR_NAME}.azurecr.io/insurance-voice-agent:v1 `
  --cpu 2 `
  --memory 4 `
  --registry-login-server ${ACR_NAME}.azurecr.io `
  --registry-username $ACR_NAME `
  --registry-password <PASSWORD> `
  --dns-name-label insurance-agent-api `
  --ports 8000
```

---

## 🎯 Next Steps

1. **Security:**
   - Add authentication to your API
   - Restrict CORS to your Vercel domain only
   - Use Azure Key Vault for API keys

2. **Performance:**
   - Enable Azure CDN for faster global access
   - Add caching for frequently asked questions
   - Optimize Docker image size

3. **Features:**
   - Add conversation history
   - Implement user sessions
   - Add analytics tracking

---

## 📝 Quick Reference

### Useful Commands

```powershell
# Restart app
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# Update Docker image
docker build -t insurance-voice-agent:v2 .
docker tag insurance-voice-agent:v2 ${ACR_NAME}.azurecr.io/insurance-voice-agent:v2
docker push ${ACR_NAME}.azurecr.io/insurance-voice-agent:v2
az webapp config container set --name $APP_NAME --resource-group $RESOURCE_GROUP --docker-custom-image-name ${ACR_NAME}.azurecr.io/insurance-voice-agent:v2

# Delete everything
az group delete --name $RESOURCE_GROUP --yes
```

### Important URLs

- Azure Portal: https://portal.azure.com
- Vercel Dashboard: https://vercel.com/dashboard
- Your Backend: `https://<app-name>.azurewebsites.net`
- Your Frontend: `https://<project-name>.vercel.app`

---

## ✅ Deployment Checklist

- [ ] Tested locally (backend + frontend)
- [ ] Created Azure resources
- [ ] Built and pushed Docker image
- [ ] Deployed to Azure App Service
- [ ] Verified backend health endpoints
- [ ] Updated frontend API_URL
- [ ] Deployed frontend to Vercel
- [ ] Tested end-to-end (text mode)
- [ ] Tested end-to-end (voice mode)
- [ ] Configured custom domain (optional)
- [ ] Set up monitoring and alerts

---

**Need Help?** Check the logs first, then review the troubleshooting section above.
