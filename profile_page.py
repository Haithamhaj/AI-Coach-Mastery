import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from firebase_config import get_user_stats

def show(language="English"):
    """
    Displays the User Profile & Progress Dashboard.
    """
    
    # Translations
    t = {
        "English": {
            "title": "My Coach Profile",
            "subtitle": "Track your journey to PCC Mastery",
            "stats": "Performance Overview",
            "hours": "Training Hours",
            "sessions": "Sessions",
            "avg_score": "Avg Score",
            "arcade_rank": "Arcade Rank",
            "competency_radar": "Competency Radar",
            "history": "Recent Activity",
            "date": "Date",
            "type": "Type",
            "score": "Score",
            "no_data": "No training data available yet. Start a session!",
            "rank_novice": "Novice Coach",
            "rank_acc": "Associate Coach (ACC)",
            "rank_pcc": "Professional Coach (PCC)",
            "rank_mcc": "Master Coach (MCC)"
        },
        "العربية": {
            "title": "ملفي ككوتش",
            "subtitle": "تتبع رحلتك نحو إتقان الكوتشينج",
            "stats": "نظرة عامة على الأداء",
            "hours": "ساعات التدريب",
            "sessions": "الجلسات",
            "avg_score": "متوسط الأداء",
            "arcade_rank": "تصنيف الأركيد",
            "competency_radar": "رادار الجدارات",
            "history": "النشاط الأخير",
            "date": "التاريخ",
            "type": "النوع",
            "score": "النتيجة",
            "no_data": "لا توجد بيانات تدريب بعد. ابدأ جلسة الآن!",
            "rank_novice": "كوتش مبتدئ",
            "rank_acc": "كوتش مشارك (ACC)",
            "rank_pcc": "كوتش محترف (PCC)",
            "rank_mcc": "كوتش خبير (MCC)"
        }
    }
    
    txt = t[language]
    
    # Get User Data
    if 'user_email' not in st.session_state:
        st.warning("Please log in to view your profile.")
        return

    user_stats = get_user_stats(st.session_state.user_email)
    
    if not user_stats:
        st.info(txt['no_data'])
        return
        
    # --- Header ---
    st.title(txt['title'])
    st.caption(txt['subtitle'])
    
    # --- Top Stats Cards ---
    st.subheader(txt['stats'])
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric(txt['hours'], f"{user_stats['total_hours']}h")
    c2.metric(txt['sessions'], user_stats['total_sessions'])
    c3.metric(txt['avg_score'], f"{user_stats['avg_score']}%")
    c4.metric(txt['arcade_rank'], user_stats['rank'])
    
    st.markdown("---")
    
    # --- Charts Section ---
    col_radar, col_history = st.columns([1, 1])
    
    with col_radar:
        st.subheader(txt['competency_radar'])
        
        # Mock Data for Radar (Replace with actual aggregation in future)
        # In a real implementation, we would aggregate scores per competency from saved sessions.
        categories = ['Ethics', 'Mindset', 'Agreements', 'Trust', 'Presence', 'Listening', 'Awareness', 'Growth']
        
        # Use a base score + some randomness or actual data if available
        # For now, we simulate a profile based on avg_score
        base_val = user_stats['avg_score']
        values = [min(100, max(20, base_val + (i%3 * 5) - 5)) for i in range(len(categories))]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='My Stats',
            line_color='#00CC96'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col_history:
        st.subheader(txt['history'])
        
        if user_stats['recent_sessions']:
            history_data = []
            for s in user_stats['recent_sessions']:
                # Format date
                created_at = s.get('created_at')
                date_str = "Unknown"
                if created_at:
                    # Handle Firestore timestamp or string
                    try:
                        date_str = created_at.strftime("%Y-%m-%d")
                    except:
                        date_str = str(created_at)[:10]
                        
                history_data.append({
                    txt['date']: date_str,
                    txt['type']: "Full Session" if s.get('mode') == 'exam' else "Training",
                    txt['score']: f"{s.get('compliance_percentage', 0)}%"
                })
            
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(txt['no_data'])
