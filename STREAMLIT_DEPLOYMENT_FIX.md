# حل مشكلة نشر التطبيق على Streamlit Cloud
# Streamlit Cloud Deployment Fix

## المشكلة / Problem
التطبيق يفشل في الاتصال على المنفذ 8501:
```
❗️ The service has encountered an error while checking the health of the Streamlit app: 
Get "http://localhost:8501/healthz": dial tcp 127.0.0.1:8501: connect: connection refused
```

## الحلول المطبقة / Applied Fixes

### 1. ✅ إصلاح المنفذ في ملف التكوين
**الملف**: `.streamlit/config.toml`
- تم تغيير المنفذ من `8080` إلى `8501`
- Streamlit Cloud يتوقع أن يعمل التطبيق على المنفذ `8501`

### 2. ✅ إضافة المكتبات المفقودة
**الملف**: `requirements.txt`
تم إضافة المكتبات التالية:
- `PyPDF2` (لقراءة ملفات PDF)
- `python-docx` (لقراءة ملفات Word)
- `striprtf` (لقراءة ملفات RTF)

### 3. 📋 التحقق من إعدادات Streamlit Cloud

يجب عليك التأكد من الإعدادات التالية في لوحة تحكم Streamlit Cloud:

#### أ. إعدادات الأسرار (Secrets)
اذهب إلى: **App Settings → Secrets**

انسخ والصق التالي واملأ القيم الحقيقية:

```toml
# Gemini API Key
GEMINI_API_KEY = "your_actual_gemini_api_key"

# Firebase Configuration
FIREBASE_API_KEY = "your_actual_firebase_api_key"
FIREBASE_PROJECT_ID = "your_actual_firebase_project_id"

# Cookie Password
COOKIE_PASSWORD = "your_secure_random_password_at_least_32_chars"

# Firebase Service Account
[firebase_service_account]
type = "service_account"
project_id = "your_project_id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_ACTUAL_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

**مهم جداً**: 
- احصل على قيم Firebase من ملف `firebase_key.json` الخاص بك
- تأكد من أن `private_key` يحتوي على `\\n` كأحرف فعلية (سيتم استبدالها في الكود)

#### ب. Python Version
تأكد من أن Python version مضبوط على `3.11` أو أعلى

#### ج. Main File Path
تأكد أن Main file path مضبوط على: `app.py`

### 4. 🔄 خطوات النشر

1. **Commit التغييرات**:
   ```bash
   git add .streamlit/config.toml requirements.txt
   git commit -m "Fix: Updated port to 8501 and added missing dependencies"
   git push origin main
   ```

2. **في Streamlit Cloud**:
   - انتقل إلى dashboard التطبيق
   - اضغط على "Reboot app" أو انتظر إعادة النشر التلقائي
   - راقب اللوجات للتأكد من عدم وجود أخطاء

### 5. 🔍 فحص الأخطاء المحتملة الأخرى

#### إذا استمرت المشكلة، تحقق من:

1. **ملف logo.jpg موجود**: 
   - يجب أن يكون في المجلد الرئيسي
   - ✅ تم التحقق - الملف موجود

2. **ملفات static/ موجودة**:
   - `static/styles.css`
   - `static/streamlit_components.css`
   - ✅ تم التحقق - الملفات موجودة

3. **جميع ملفات Python موجودة**:
   ```
   ✅ translations.py
   ✅ marker_helpers.py
   ✅ admin_middleware.py
   ✅ user_dashboard.py
   ✅ auth_handler.py
   ✅ firebase_config.py
   ✅ analysis_engine.py
   ✅ training_engine.py
   ✅ pdf_renderer.py
   ✅ admin_dashboard.py
   ```

4. **ملف markers.json موجود**:
   - ✅ تم التحقق - الملف موجود

### 6. 📊 مراقبة اللوجات

في Streamlit Cloud، راقب اللوجات بحثاً عن:
- ❌ Import errors
- ❌ Missing file errors
- ❌ API key errors
- ✅ Success messages

### 7. 🎯 الخطوات التالية

بعد تطبيق هذه الإصلاحات:

1. Push التغييرات إلى GitHub
2. انتظر إعادة نشر Streamlit Cloud (تلقائياً)
3. تحقق من اللوجات
4. إذا استمرت المشكلة، شارك اللوجات الكاملة

## ملاحظات إضافية

### حول Firebase Secrets
الكود يقوم بإنشاء `firebase_key.json` تلقائياً من Streamlit secrets:
```python
if not os.path.exists("firebase_key.json"):
    if hasattr(st, 'secrets') and "firebase_service_account" in st.secrets:
        key_dict = dict(st.secrets["firebase_service_account"])
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        with open("firebase_key.json", "w") as f:
            json.dump(key_dict, f)
```

### حول المنفذ
- Streamlit Cloud **دائماً** يستخدم المنفذ `8501`
- أي منفذ آخر سيسبب فشل health check

## الخلاصة

التغييرات الرئيسية المطلوبة:
1. ✅ المنفذ → 8501 في `.streamlit/config.toml`
2. ✅ إضافة المكتبات المفقودة في `requirements.txt`
3. ⏳ إعداد Secrets في Streamlit Cloud dashboard
4. ⏳ Push التغييرات ومراقبة النشر
