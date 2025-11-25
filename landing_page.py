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
# RENAMED to v2 to force cache invalidation
@st.cache_data
def get_landing_html_v3(language):
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
        # Robust language check
        is_arabic = "ar" in language.lower() or "عربي" in language
        target_lang = 'ar' if is_arabic else 'en'
        
        # Inject Initial Language State for index.html to pick up
        js_code = f"""
        <script>
            window.initialLang = "{target_lang}";
            
            document.addEventListener('DOMContentLoaded', function() {{
                // Handle Buttons (CTA Logic Only - Language logic is now native in index.html)
                const buttons = document.querySelectorAll('a[href="#login"], button, .cta-button');
                buttons.forEach(btn => {{
                    btn.addEventListener('click', function(e) {{
                        const text = btn.innerText.toLowerCase();
                        if (text.includes('ابدأ') || text.includes('start') || text.includes('login') || btn.getAttribute('href') === '#login') {{
                            e.preventDefault();
                            window.parent.postMessage({{type: 'streamlit:set_component_value', value: 'start_login'}}, '*');
                        }}
                    }});
                }});
            }});
        </script>
        """
        
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
    html_content = get_landing_html_v3(language)

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
