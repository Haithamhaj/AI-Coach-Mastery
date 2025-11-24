"""
Admin Dashboard Page - Analytics and User Management
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from admin_middleware import get_admin_middleware
from admin_analytics import get_admin_analytics
from translations import translations

def show_admin_dashboard():
    """Main admin dashboard page"""
    # Get language
    language = st.session_state.get('language', 'English')
    t = translations.get(language, translations["English"])
    
    # Check admin access
    admin = get_admin_middleware()
    if not admin.require_admin():
        return
    
    # Get analytics instance
    analytics = get_admin_analytics()
    
    # Header
    st.title("📊 Admin Dashboard" if language == "English" else "📊 لوحة تحكم الأدمن")
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data" if language == "English" else "🔄 تحديث البيانات"):
        st.rerun()
    
    # Get overall stats
    stats = analytics.get_total_stats()
    
    # Overview Cards
    st.subheader("📈 Overview" if language == "English" else "📈 نظرة عامة")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Users" if language == "English" else "إجمالي المستخدمين",
            value=stats.get('total_users', 0)
        )
    
    with col2:
        st.metric(
            label="Active (30d)" if language == "English" else "نشطين (30 يوم)",
            value=stats.get('active_users_30d', 0)
        )
    
    with col3:
        st.metric(
            label="Total Sessions" if language == "English" else "إجمالي الجلسات",
            value=stats.get('total_sessions', 0)
        )
    
    with col4:
        st.metric(
            label="Est. Cost" if language == "English" else "التكلفة التقديرية",
            value=f"${stats.get('total_cost', 0):.2f}"
        )
    
    st.markdown("---")
    
    # --- FILTERS SECTION ---
    st.subheader("🔍 Filters" if language == "English" else "🔍 الفلاتر")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        # Time range filter
        time_range = st.selectbox(
            "Time Period" if language == "English" else "الفترة الزمنية",
            options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"],
            index=1,  # Default to 30 days
            key="time_range_filter"
        )
        
        # Map display names to actual days
        time_map = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90
        }
        
        if time_range == "Custom":
            custom_days = st.number_input(
                "Days" if language == "English" else "أيام",
                min_value=1,
                max_value=365,
                value=30
            )
            selected_days = custom_days
        else:
            selected_days = time_map[time_range]
    
    with filter_col2:
        # Service type filter
        all_services = analytics.get_token_usage_by_service()
        service_options = ["All Services"] + list(all_services.keys())
        
        selected_service = st.selectbox(
            "Service Type" if language == "English" else "نوع الخدمة",
            options=service_options,
            key="service_filter"
        )
    
    with filter_col3:
        # Quick stats for filtered data
        if selected_service != "All Services" and selected_service in all_services:
            service_data = all_services[selected_service]
            st.metric(
                label=f"{selected_service} Tokens",
                value=f"{service_data['tokens']:,}",
                delta=f"${service_data['cost']:.4f}"
            )
        else:
            st.metric(
                label="Selected Period",
                value=f"{selected_days} days"
            )
    
    st.markdown("---")
    
    # Token Usage by Service (with filters applied)
    st.subheader("🔥 Token Usage by Service" if language == "English" else "🔥 استهلاك Tokens حسب الخدمة")
    
    # Get filtered usage data
    usage_by_service = analytics.get_token_usage_by_service_filtered(
        days=selected_days,
        service_type=selected_service if selected_service != "All Services" else None
    )
    
    if usage_by_service:
        # Create dataframe
        service_data = []
        for service, data in usage_by_service.items():
            service_data.append({
                'Service': service,
                'Tokens': data['tokens'],
                'Cost': data['cost'],
                'Calls': data['count']
            })
        
        df_services = pd.DataFrame(service_data)
        
        # Pie chart for token distribution
        fig_pie = px.pie(
            df_services,
            values='Tokens',
            names='Service',
            title=f'Token Distribution ({time_range})' if language == "English" else f'توزيع Tokens ({time_range})',
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Service breakdown table
        st.dataframe(
            df_services.style.format({
                'Tokens': '{:,.0f}',
                'Cost': '${:.4f}',
                'Calls': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No usage data available for selected filters" if language == "English" else "لا توجد بيانات للفلاتر المحددة")
    
    st.markdown("---")
    
    # Usage Over Time (with filters applied)
    st.subheader(f"📊 Usage Over Time ({time_range})" if language == "English" else f"📊 الاستخدام عبر الوقت ({time_range})")
    
    usage_timeline = analytics.get_usage_over_time(days=selected_days)
    
    if usage_timeline:
        # Convert to dataframe
        timeline_data = []
        for date, data in sorted(usage_timeline.items()):
            timeline_data.append({
                'Date': date,
                'Tokens': data['tokens'],
                'Cost': data['cost'],
                'Calls': data['calls']
            })
        
        df_timeline = pd.DataFrame(timeline_data)
        
        # Line chart for tokens over time
        fig_line = go.Figure()
        
        fig_line.add_trace(go.Scatter(
            x=df_timeline['Date'],
            y=df_timeline['Tokens'],
            mode='lines+markers',
            name='Tokens Used',
            line=dict(color='#06b6d4', width=3),
            marker=dict(size=8)
        ))
        
        fig_line.update_layout(
            title='Daily Token Usage',
            xaxis_title='Date',
            yaxis_title='Tokens',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Cost over time
        fig_cost = px.area(
            df_timeline,
            x='Date',
            y='Cost',
            title='Daily Cost',
            color_discrete_sequence=['#3b82f6']
        )
        fig_cost.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff'
        )
        
        st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.info("No timeline data available yet" if language == "English" else "لا توجد بيانات زمنية بعد")
    
    st.markdown("---")
    
    # Top Users
    st.subheader("👥 Top Users" if language == "English" else "👥 أكثر المستخدمين نشاطاً")
    
    top_users = analytics.get_top_users(limit=10)
    
    if top_users:
        # Convert to dataframe
        df_users = pd.DataFrame(top_users)
        
        # Format last activity
        df_users['last_activity'] = df_users['last_activity'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notnull(x) else 'N/A'
        )
        
        # Display table
        st.dataframe(
            df_users[['email', 'total_sessions', 'total_tokens', 'total_cost', 'last_activity']].style.format({
                'total_tokens': '{:,.0f}',
                'total_cost': '${:.4f}',
                'total_sessions': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No user data available yet" if language == "English" else "لا توجد بيانات مستخدمين بعد")
    
    st.markdown("---")
    
    # User Search and Details
    st.subheader("🔍 User Search" if language == "English" else "🔍 بحث عن مستخدم")
    
    search_term = st.text_input(
        "Search by email" if language == "English" else "البحث بالبريد الإلكتروني",
        placeholder="user@example.com"
    )
    
    if search_term:
        search_results = analytics.search_users(search_term)
        
        if search_results:
            st.success(f"Found {len(search_results)} user(s)" if language == "English" else f"تم العثور على {len(search_results)} مستخدم")
            
            for user in search_results:
                with st.expander(f"👤 {user['email']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Role:** {user['role']}")
                        st.write(f"**Total Sessions:** {user['usage_stats'].get('total_sessions', 0)}")
                        st.write(f"**Total Tokens:** {user['usage_stats'].get('total_tokens', 0):,}")
                    
                    with col2:
                        st.write(f"**Total Cost:** ${user['usage_stats'].get('total_cost', 0):.4f}")
                        last_activity = user['usage_stats'].get('last_activity')
                        if last_activity:
                            st.write(f"**Last Activity:** {last_activity.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Show progress chart
                    progress_data = analytics.get_user_progress(user['email'])
                    
                    if progress_data:
                        st.markdown("**Progress Over Time:**")
                        
                        df_progress = pd.DataFrame(progress_data)
                        
                        fig_progress = px.line(
                            df_progress,
                            x='timestamp',
                            y='score',
                            title='Session Scores',
                            markers=True,
                            color_discrete_sequence=['#06b6d4']
                        )
                        fig_progress.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#ffffff'
                        )
                        
                        st.plotly_chart(fig_progress, use_container_width=True)
                    
                    # Show usage by service
                    from token_tracker import get_token_tracker
                    tracker = get_token_tracker()
                    user_service_usage = tracker.get_user_usage_by_service(user['email'])
                    
                    if user_service_usage:
                        st.markdown("**Usage by Service:**")
                        
                        service_rows = []
                        for service, data in user_service_usage.items():
                            service_rows.append({
                                'Service': service,
                                'Tokens': data['tokens'],
                                'Cost': f"${data['cost']:.4f}",
                                'Calls': data['count']
                            })
                        
                        st.table(pd.DataFrame(service_rows))
        else:
            st.warning("No users found" if language == "English" else "لم يتم العثور على مستخدمين")
    
    st.markdown("---")
    
    # Export Data
    st.subheader("📥 Export Data" if language == "English" else "📥 تصدير البيانات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export All Users (CSV)" if language == "English" else "📊 تصدير جميع المستخدمين (CSV)"):
            # Get all users
            all_users = analytics.get_top_users (limit=1000)  # Get all
            
            if all_users:
                df_export = pd.DataFrame(all_users)
                csv = df_export.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"users_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("💰 Export Usage Summary (CSV)" if language == "English" else "💰 تصدير ملخص الاستخدام (CSV)"):
            usage_summary = analytics.get_token_usage_by_service()
            
            if usage_summary:
                summary_data = []
                for service, data in usage_summary.items():
                    summary_data.append({
                        'Service': service,
                        'Total Tokens': data['tokens'],
                        'Total Cost': data['cost'],
                        'API Calls': data['count']
                    })
                
                df_summary = pd.DataFrame(summary_data)
                csv = df_summary.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"usage_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
