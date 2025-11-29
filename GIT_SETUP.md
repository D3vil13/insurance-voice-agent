# 🚀 Git Setup and GitHub Upload Guide

## Step-by-Step Instructions

### Step 1: Check if Git is Installed

```powershell
git --version
```

**If not installed:**
```powershell
winget install Git.Git
```

Or download from: https://git-scm.com/downloads

---

### Step 2: Configure Git (First Time Only)

```powershell
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"

# Verify
git config --list
```

---

### Step 3: Initialize Git Repository

```powershell
# Navigate to project
cd c:\Users\d3vsh\Downloads\backupMH

# Initialize Git
git init

# Check status
git status
```

---

### Step 4: Add Files to Git

```powershell
# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status
```

---

### Step 5: Create First Commit

```powershell
# Commit with message
git commit -m "Initial commit: Insurance Voice Agent"

# Verify commit
git log --oneline
```

---

### Step 6: Create GitHub Repository

1. Go to https://github.com
2. Click "+" → "New repository"
3. Name: `insurance-voice-agent`
4. Description: "AI-powered voice assistant for insurance customer service"
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

---

### Step 7: Connect to GitHub

**Copy the commands from GitHub, or use these:**

```powershell
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/insurance-voice-agent.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

**If you get "master" instead of "main":**
```powershell
git branch -M main
git push -u origin main
```

---

### Step 8: Verify Upload

1. Go to https://github.com/YOUR_USERNAME/insurance-voice-agent
2. You should see all your files!
3. Check that `apikeys.env` is NOT there (it's in .gitignore)

---

## 🔒 Security Checklist

Before pushing, verify these files are NOT included:

- ❌ `apikeys.env` (contains your API key)
- ❌ `logs/` folder (contains logs)
- ❌ `api_audio_output/` (generated audio)
- ❌ `__pycache__/` (Python cache)

**These are automatically excluded by `.gitignore`**

---

## 📝 Future Updates

After making changes:

```powershell
# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

---

## 🌿 Branching (Optional)

```powershell
# Create new branch for feature
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push branch
git push -u origin feature/new-feature

# Then create Pull Request on GitHub
```

---

## 🔄 Clone on Another Machine

```powershell
# Clone repository
git clone https://github.com/YOUR_USERNAME/insurance-voice-agent.git

# Navigate to folder
cd insurance-voice-agent

# Install dependencies
pip install -r requirements.txt

# Copy and configure API keys
cp apikeys.env.example apikeys.env
# Edit apikeys.env with your key

# Run
.\start_local.bat
```

---

## ⚠️ Important Notes

1. **Never commit API keys** - They're in `.gitignore`
2. **Use `apikeys.env.example`** - For sharing template
3. **Large files** - ChromaDB might be large, consider Git LFS if needed
4. **Sensitive data** - Double-check before pushing

---

## 🆘 Common Issues

### "Permission denied (publickey)"

Use HTTPS instead of SSH:
```powershell
git remote set-url origin https://github.com/YOUR_USERNAME/insurance-voice-agent.git
```

### "Repository not found"

Check repository name and your username:
```powershell
git remote -v
# Should show: https://github.com/YOUR_USERNAME/insurance-voice-agent.git
```

### Accidentally committed API key

```powershell
# Remove from Git history (be careful!)
git rm --cached apikeys.env
git commit -m "Remove API keys"
git push

# Then regenerate your API key on OpenRouter!
```

---

## ✅ Checklist

- [ ] Git installed
- [ ] Git configured (name, email)
- [ ] Repository initialized (`git init`)
- [ ] Files added (`git add .`)
- [ ] First commit created
- [ ] GitHub repository created
- [ ] Remote added
- [ ] Pushed to GitHub
- [ ] Verified on GitHub
- [ ] API keys NOT visible on GitHub

---

**You're all set!** 🎉

Your project is now on GitHub at:
`https://github.com/YOUR_USERNAME/insurance-voice-agent`
