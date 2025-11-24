import streamlit as st
import base64
import os

# Cache the image loading to improve speed
@st.cache_data
def get_image_base64(image_path):
    """Read image file and convert to base64 string"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""
    except Exception as e:
        return ""

# Cache the HTML preparation to improve speed
@st.cache_data
def get_landing_html(language):
    """Prepare the HTML content with embedded images and JS"""
    try:
        # Read the original HTML file
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # --- 1. Embed Images as Base64 ---
        # Logo
        logo_b64 = get_image_base64("logo.jpg")
        if logo_b64:
            html_content = html_content.replace('src="logo.jpg"', f'src="data:image/jpeg;base64,{logo_b64}"')
            
        # Feature Images
        for img_name in ["feature1.png", "feature2.png", "feature3.png"]:
            img_b64 = get_image_base64(img_name)
            if img_b64:
                html_content = html_content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{img_b64}"')

        # --- 2. Fix Layout (Full Width Navbar) ---
        html_content = html_content.replace('max-w-7xl mx-auto', 'w-full px-6 md:px-12 mx-auto')

        # --- 3. Enforce Language & Interaction ---
        target_lang = 'ar' if language == "العربية" else 'en'
        
        # CRITICAL FIX: Modify HTML directly before rendering to ensure correct direction
        # This prevents "flash of wrong direction" and ensures English is LTR, Arabic is RTL
        if target_lang == 'en':
            html_content = html_content.replace('dir="rtl"', 'dir="ltr"')
            html_content = html_content.replace('lang="ar"', 'lang="en"')
        else:
            # Ensure it's RTL for Arabic (in case the file was changed)
            html_content = html_content.replace('dir="ltr"', 'dir="rtl"')
            html_content = html_content.replace('lang="en"', 'lang="ar"')
        
        js_code = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // 1. Handle Language
                const targetLang = 'TARGET_LANG_PLACEHOLDER';
                const htmlRoot = document.getElementById('html-root');
                
                function setLanguage(lang) {
                    if (!htmlRoot) return;
                    
                    // STRICT STANDARD LOGIC
                    // Arabic = RTL (Right to Left)
                    // English = LTR (Left to Right)
                    
                    if (lang === 'ar') {
                        htmlRoot.setAttribute('lang', 'ar');
                        htmlRoot.setAttribute('dir', 'rtl');
                        document.body.style.direction = 'rtl';
                        document.body.style.textAlign = 'right';
                        
                        // Ensure container alignment
                        const containers = document.querySelectorAll('.max-w-7xl');
                        containers.forEach(el => el.style.direction = 'rtl');
                        
                        if (typeof updateContent === 'function') updateContent('ar');
                    } else {
                        htmlRoot.setAttribute('lang', 'en');
                        htmlRoot.setAttribute('dir', 'ltr');
                        document.body.style.direction = 'ltr';
                        document.body.style.textAlign = 'left';
                        
                        // Ensure container alignment
                        const containers = document.querySelectorAll('.max-w-7xl');
                        containers.forEach(el => el.style.direction = 'ltr');
                        
                        if (typeof updateContent === 'function') updateContent('en');
                    }
                }
                
                // Ensure JS also enforces the correct language
                setLanguage(targetLang);
                
                // 2. Handle Buttons
                const buttons = document.querySelectorAll('a[href="#login"], button, .cta-button');
                buttons.forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        const text = btn.innerText.toLowerCase();
                        if (text.includes('ابدأ') || text.includes('start') || text.includes('login') || btn.getAttribute('href') === '#login') {
                            e.preventDefault();
                            window.parent.postMessage({type: 'streamlit:set_component_value', value: 'start_login'}, '*');
                        }
                    });
                });
                
                // 3. Handle Language Toggle
                const langBtn = document.getElementById('langToggle');
                if (langBtn) {
                    langBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        const currentDir = htmlRoot.getAttribute('dir');
                        const newLang = currentDir === 'rtl' ? 'en' : 'ar';
                        setLanguage(newLang);
                    });
                }
            });
        </script>
        """
        js_code = js_code.replace('TARGET_LANG_PLACEHOLDER', target_lang)
        
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", js_code + "</body>")
        else:
            html_content += js_code
            
        return html_content
    except Exception as e:
        return None

def show_landing_page(language="English"):
    """Display the landing page"""
    
    # CSS to remove ALL whitespace and padding
    st.markdown("""
        <style>
        /* Hide Sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* Remove all padding/margins from the main block container */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        
        /* Hide the Streamlit header */
        header[data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
        }
        
        /* Force iframe to be fixed and cover everything */
        iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            z-index: 1 !important;
            display: block !important;
        }
        
        /* Ensure the fallback button stays on top if needed */
        .stButton {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 99999 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Get cached HTML
    html_content = get_landing_html(language)

    if html_content:
        import streamlit.components.v1 as components
        # Render HTML
        components.html(html_content, height=1200, scrolling=True)
        
        # Fallback Login Button (Styled to float)
        # We use a container to place the button, but CSS handles positioning
        if st.button("🚀 تسجيل الدخول / Login", type="primary", key="fallback_login"):
            st.session_state.show_landing = False
            st.rerun()
    else:
        st.error("ملف التصميم الأصلي (index.html) غير موجود.")
        if st.button("Login"):
            st.session_state.show_landing = False
            st.rerun()
