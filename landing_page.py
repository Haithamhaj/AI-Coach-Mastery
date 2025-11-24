import streamlit as st
import base64
import os

def get_image_base64(image_path):
    """Read image file and convert to base64 string"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""
    except Exception as e:
        return ""

def show_landing_page(language="English"):
    """Display the landing page with embedded original HTML"""
    
    # Hide sidebar and adjust layout
    # NOTE: Commented out aggressive hiding to debug blank screen issue
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        
        /* Ensure iframe takes full width and height */
        iframe {
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            display: block !important;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        # Check if file exists
        if not os.path.exists('index.html'):
            st.error("Error: index.html not found!")
            return

        # Read the original HTML file
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Debug: Print first 100 chars to verify read (will be visible if CSS doesn't hide it)
        # st.write(f"Read {len(html_content)} bytes from index.html") 

            
        # --- 1. Embed Images as Base64 ---
        # Logo
        logo_b64 = get_image_base64("logo.jpg")
        if logo_b64:
            # Replace logo src specifically
            html_content = html_content.replace('src="logo.jpg"', f'src="data:image/jpeg;base64,{logo_b64}"')
            
        # Feature Images
        for img_name in ["feature1.png", "feature2.png", "feature3.png"]:
            img_b64 = get_image_base64(img_name)
            if img_b64:
                html_content = html_content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{img_b64}"')

        # --- 2. Fix Layout (Full Width Navbar) ---
        # Remove max-w-7xl from navbar to make it full width if requested
        html_content = html_content.replace('max-w-7xl mx-auto', 'w-full px-6 md:px-12 mx-auto')

        # --- 3. Enforce Language & Interaction ---
        # Determine target language code for JS
        target_lang = 'ar' if language == "العربية" else 'en'
        
        # JS Code to inject - using standard string to avoid f-string brace issues
        js_code = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // 1. Handle Language
                const targetLang = 'TARGET_LANG_PLACEHOLDER';
                const htmlRoot = document.getElementById('html-root');
                
                // Function to set language
                function setLanguage(lang) {
                    if (!htmlRoot) return;
                    
                    if (lang === 'ar') {
                        htmlRoot.setAttribute('lang', 'ar');
                        htmlRoot.setAttribute('dir', 'rtl');
                        document.body.style.direction = 'rtl';
                        // Trigger any existing translation logic if available
                        if (typeof updateContent === 'function') updateContent('ar');
                    } else {
                        htmlRoot.setAttribute('lang', 'en');
                        htmlRoot.setAttribute('dir', 'ltr');
                        document.body.style.direction = 'ltr';
                        if (typeof updateContent === 'function') updateContent('en');
                    }
                }
                
                // Set initial language
                setLanguage(targetLang);
                
                // 2. Handle Buttons (Start/Login)
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
                
                // 3. Handle Language Toggle Button Click
                const langBtn = document.getElementById('langToggle');
                if (langBtn) {
                    langBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        // Toggle local state
                        const currentDir = htmlRoot.getAttribute('dir');
                        const newLang = currentDir === 'rtl' ? 'en' : 'ar';
                        setLanguage(newLang);
                    });
                }
            });
        </script>
        """
        
        # Replace placeholder with actual language
        js_code = js_code.replace('TARGET_LANG_PLACEHOLDER', target_lang)
        
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", js_code + "</body>")
        else:
            html_content += js_code

        # Display the HTML
        import streamlit.components.v1 as components
        
        # Render HTML with full height and width
        components.html(html_content, height=1200, scrolling=True)
        
        # --- Floating Login Button (Fallback) ---
        st.markdown("""
        <style>
        .floating-login-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🚀 تسجيل الدخول / Login", type="primary", use_container_width=True):
                    st.session_state.show_landing = False
                    st.rerun()

    except FileNotFoundError:
        st.error("ملف التصميم الأصلي (index.html) غير موجود.")
        if st.button("Login"):
            st.session_state.show_landing = False
            st.rerun()
