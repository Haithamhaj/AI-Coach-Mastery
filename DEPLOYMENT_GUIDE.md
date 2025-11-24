# 🚀 دليل نشر التطبيق - AI Coach Mastery

## الطريقة 1: Streamlit Cloud (مجاني وسريع) ⭐

### الخطوات:

#### 1. رفع الكود على GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

#### 2. نشر على Streamlit Cloud
1. اذهب إلى: https://streamlit.io/cloud
2. سجل دخول بحساب GitHub
3. اضغط "New app"
4. اختر الريبو: `AI-Coach-Mastery`
5. Main file: `app.py`
6. اضغط "Deploy"

#### 3. إضافة Secrets (المتغيرات السرية)
في Streamlit Cloud Dashboard:
- Settings → Secrets
- أضف متغيرات `.env`:
```toml
GEMINI_API_KEY = "your_key_here"
FIREBASE_API_KEY = "your_key_here"
FIREBASE_PROJECT_ID = "your_project_id"
FIREBASE_STORAGE_BUCKET = "your_bucket"
FIREBASE_MESSAGING_SENDER_ID = "your_sender_id"
FIREBASE_APP_ID = "your_app_id"
```

#### 4. نشر صفحة الهبوط (index.html)
على **Netlify**:
1. اذهب إلى: https://app.netlify.com
2. اسحب المجلد الذي يحتوي على:
   - `index.html`
   - `logo.jpg`
   - الصور الأخرى
3. عدّل رابط الزر في `index.html`:
```html
<!-- استبدل localhost بـ رابط Streamlit Cloud -->
<a href="https://your-app.streamlit.app">Start Your Journey</a>
```

---

## الطريقة 2: Google Cloud Run (احترافي)

### المتطلبات:
- حساب Google Cloud
- تفعيل Cloud Run API
- تثبيت Google Cloud CLI

### الخطوات:

#### 1. إعداد المشروع
```bash
# تسجيل الدخول
gcloud auth login

# إنشاء مشروع جديد (أو استخدام موجود)
gcloud projects create ai-coach-mastery
gcloud config set project ai-coach-mastery

# تفعيل APIs المطلوبة
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### 2. بناء ورفع Docker Image
```bash
# بناء الصورة
gcloud builds submit --tag gcr.io/ai-coach-mastery/ai-coach-app

# أو محلياً:
docker build -t gcr.io/ai-coach-mastery/ai-coach-app .
docker push gcr.io/ai-coach-mastery/ai-coach-app
```

#### 3. النشر على Cloud Run
```bash
gcloud run deploy ai-coach-mastery \
  --image gcr.io/ai-coach-mastery/ai-coach-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key,FIREBASE_API_KEY=your_key \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 1
```

#### 4. إضافة Domain مخصص (اختياري)
```bash
# ربط Domain
gcloud run domain-mappings create \
  --service ai-coach-mastery \
  --domain coach.yourdomain.com \
  --region us-central1
```

---

## الطريقة 3: Heroku (سهل)

### الخطوات:

#### 1. تثبيت Heroku CLI
```bash
brew tap heroku/brew && brew install heroku
```

#### 2. إنشاء ملف `setup.sh`
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = \$PORT\n\
" > ~/.streamlit/config.toml
```

#### 3. إنشاء `Procfile`
```
web: sh setup.sh && streamlit run app.py
```

#### 4. النشر
```bash
heroku login
heroku create ai-coach-mastery
git push heroku main
heroku config:set GEMINI_API_KEY=your_key
heroku config:set FIREBASE_API_KEY=your_key
```

---

## ⚙️ المتغيرات البيئية المطلوبة

تأكد من إضافة هذه المتغيرات في أي منصة:

```
GEMINI_API_KEY=<your_gemini_api_key>
FIREBASE_API_KEY=<your_firebase_api_key>
FIREBASE_PROJECT_ID=<your_project_id>
FIREBASE_STORAGE_BUCKET=<your_storage_bucket>
FIREBASE_MESSAGING_SENDER_ID=<your_sender_id>
FIREBASE_APP_ID=<your_app_id>
FIREBASE_MEASUREMENT_ID=<your_measurement_id>
```

---

## 🔒 الأمان والـ Secrets

### لـ Firebase Key:
**لا ترفع `firebase_key.json` على GitHub!**

بدلاً من ذلك:
1. حوّل المحتوى لـ base64:
```bash
cat firebase_key.json | base64
```

2. أضفه كـ environment variable:
```
FIREBASE_KEY_BASE64=<base64_encoded_content>
```

3. في الكود، فك التشفير:
```python
import base64
import json
import os

firebase_key = json.loads(
    base64.b64decode(os.getenv("FIREBASE_KEY_BASE64"))
)
```

---

## 📊 المقارنة بين الطرق

| المنصة | التكلفة | السهولة | المميزات |
|--------|---------|---------|----------|
| **Streamlit Cloud** | مجاني | ⭐⭐⭐⭐⭐ | سهل جداً، مثالي للبداية |
| **Google Cloud Run** | من $0 | ⭐⭐⭐ | Scalable، احترافي |
| **Heroku** | من $7/شهر | ⭐⭐⭐⭐ | سهل، موثوق |
| **AWS/Azure** | متغير | ⭐⭐ | قوي لكن معقد |

---

## 🎯 التوصية

**للبداية:** استخدم **Streamlit Cloud** للتطبيق + **Netlify** لصفحة الهبوط (كلاهما مجاني!)

**للإنتاج:** استخدم **Google Cloud Run** مع Custom Domain

---

## 📝 ملاحظات مهمة

1. **قبل النشر:**
   - ✅ تأكد من `.gitignore` يشمل `.env` و `firebase_key.json`
   - ✅ راجع جميع الـ API Keys
   - ✅ اختبر التطبيق محلياً

2. **بعد النشر:**
   - ✅ اختبر جميع المميزات
   - ✅ ت��كد من Firebase متصل
   - ✅ راقب الـ logs للأخطاء

3. **الأداء:**
   - استخدم caching في Streamlit
   - قلل حجم الصور
   - استخدم CDN للملفات الثابتة

---

## 🆘 المساعدة

إذا واجهت مشاكل:
- راجع Logs في المنصة المستخدمة
- تأكد من جميع المتغيرات البيئية صحيحة
- تأكد من `requirements.txt` محدث
