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
        
        if is_arabic:
            # --- MANUAL LAYOUT SWAP FOR ARABIC ---
            # Instead of relying on dir="rtl" which seems flaky in this context,
            # we will manually swap the visual order of the columns.
            # Current: Text is order-1, Image is order-2.
            # Desired in Arabic: Text on Right, Image on Left.
            # In a standard LTR grid: [Left Element] [Right Element]
            # So we want: [Image] [Text] -> Image Left, Text Right.
            # So Image needs to be first (order-1) and Text needs to be second (order-2).
            
            # Swap order-1 and order-2
            # Use placeholders to avoid double replacement
            html_content = html_content.replace('order-1', 'ORDER_PLACEHOLDER_1')
            html_content = html_content.replace('order-2', 'ORDER_PLACEHOLDER_2')
            
            html_content = html_content.replace('ORDER_PLACEHOLDER_1', 'order-2') # Text becomes order-2 (Right in LTR)
            html_content = html_content.replace('ORDER_PLACEHOLDER_2', 'order-1') # Image becomes order-1 (Left in LTR)
            
            # Force Text Alignment to Right
            html_content = html_content.replace('text-left', 'text-right') # If any
            # Inject explicit text-right class to the text container
            html_content = html_content.replace('class="order-2 space-y-8', 'class="order-2 space-y-8 text-right')
            
            # Flip the Navbar logic too if needed, but let's stick to the main hero first.
            
        # CSS to FORCE direction (The Nuclear Option) - Still keep this for other elements
        direction = "rtl" if is_arabic else "ltr"
        align = "right" if is_arabic else "left"
        
        # Enhanced CSS for RTL
        force_css = f"""
        <style>
            html, body, #html-root {{
                direction: {direction} !important;
                text-align: {align} !important;
            }}
            /* Force grid and flex containers to respect direction */
            .grid, .flex, .wave-text, .space-y-8, .space-y-2 {{
                direction: {direction} !important;
            }}
            
            /* Explicitly handle text alignment for content */
            h1, h2, h3, h4, p, .text-slate-300, .text-slate-400 {{
                text-align: {align} !important;
            }}
            
            /* Fix navbar alignment */
            nav {{
                direction: {direction} !important;
            }}
            
            /* Ensure icons in buttons flip correctly if needed */
            .group svg {{
                transform: { "scaleX(-1)" if is_arabic else "none" };
            }}
        </style>
        """
        
        # Inject CSS at the beginning of head
        html_content = html_content.replace('<head>', f'<head>{force_css}')
        
        # Also try to fix the attributes just in case
        if target_lang == 'en':
            html_content = html_content.replace('dir="rtl"', 'dir="ltr"')
            html_content = html_content.replace('lang="ar"', 'lang="en"')
        else:
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
                    
                    const isAr = lang === 'ar';
                    const dir = isAr ? 'rtl' : 'ltr';
                    const align = isAr ? 'right' : 'left';
                    
                    htmlRoot.setAttribute('lang', lang);
                    htmlRoot.setAttribute('dir', dir);
                    document.body.style.direction = dir;
                    document.body.style.textAlign = align;
                    
                    // Force all grids and flex containers
                    document.querySelectorAll('.grid, .flex').forEach(el => {
                        el.style.direction = dir;
                    });
                    
                    // Force text alignment
                    document.querySelectorAll('h1, h2, h3, h4, p').forEach(el => {
                        el.style.textAlign = align;
                    });
                    
                    // Fix Icons mirroring in RTL
                    if (isAr) {
                        document.querySelectorAll('svg.feather, svg.lucide').forEach(svg => {
                            svg.style.transform = 'scaleX(-1)';
                        });
                    }
                }
                
                // Initial set
                setLanguage(targetLang);
                
                // Aggressive enforcement (every 500ms for 5 seconds) to fight race conditions
                let attempts = 0;
                const interval = setInterval(() => {
                    setLanguage(targetLang);
                    attempts++;
                    if (attempts > 10) clearInterval(interval);
                }, 500);
                
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
