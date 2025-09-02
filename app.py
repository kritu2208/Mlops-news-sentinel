import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set matplotlib style
plt.style.use('default')
sns.set_palette("pastel")

# Page configuration
st.set_page_config(
    page_title="NewsPulse AI Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful coordinated gradient theme
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 60%, #415a77 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

h1, h2, h3, h4, h5, h6, .main-header, .section-header {
    font-weight: 900 !important;
    letter-spacing: -1px;
    color: #f0f0f0 !important; /* Near white for readability */
    text-shadow: 0 0 6px rgba(0,0,0,0.7);
}

.main-header {
    font-size: 4rem !important;
    background: linear-gradient(135deg, #fefefe 0%, #ffd166 100%) !important; /* soft cream to gold */
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 1rem !important;
    text-align: center !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

.section-header {
    font-size: 2.5rem !important;
    border-left: 8px solid #ffd166; /* softer gold */
    padding-left: 25px !important;
    background: linear-gradient(135deg, #f9f9f9 0%, #fffdfa 100%) !important;
    padding: 20px 25px !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    margin-bottom: 2.5rem !important;
}

p, .bold-paragraph, ul, li {
    font-weight: 700 !important;
    font-size: 1.18rem !important;
    color: #dedede !important; /* off-white for text */
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

.main-container {
    background: rgba(239, 239, 239, 0.95);
    border-radius: 24px;
    padding: 35px;
    margin: 25px 0;
    box-shadow: 0 20px 50px rgba(15, 24, 39, 0.3);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 209, 89, 0.4);
}

.metric-card {
    background: linear-gradient(135deg, #fffefc 0%, #fff9f0 100%);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin: 15px;
    box-shadow: 0 10px 35px rgba(255, 209, 89, 0.25);
    border: 2px solid rgba(255, 209, 89, 0.3);
    transition: all 0.4s ease;
    min-height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    word-wrap: break-word;
    white-space: normal;
}

.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 45px rgba(255, 209, 89, 0.4);
}

.metric-value {
    font-size: 3.2rem;
    font-weight: 900;
    color: #1b263b; /* dark navy */
    margin-bottom: 10px;
    line-height: 1.1;
    font-family: 'Inter', sans-serif;
}

.metric-label {
    font-size: 1.2rem;
    color: #c9a44d; /* warm gold */
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Inter', sans-serif;
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: normal;
}

/* Sidebar */
.css-1d391kg {
    background: linear-gradient(135deg, #1b263b 0%, #415a77 100%) !important;
    backdrop-filter: blur(15px);
    border-right: 3px solid rgba(255, 209, 89, 0.3);
    color: #f0f0f0 !important;
}

/* Filter section */
.filter-section {
    background: linear-gradient(135deg, #415a77 0%, #ffd166 100%);
    padding: 25px;
    border-radius: 20px;
    color: #1b263b;
    margin-bottom: 25px;
}

/* Article cards */
.article-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f8f8 100%);
    border-radius: 20px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(15, 24, 39, 0.15);
    border: 2px solid rgba(255, 209, 89, 0.3);
    transition: all 0.3s ease;
    color: #1b263b !important; /* Dark navy for all text */
    font-weight: 700 !important; /* Enhance weight for readability */
}
.article-card h3 {
    color: #1b263b !important;
    font-weight: 900 !important;
    text-shadow: none !important; /* Remove if present */
}
.article-card p {
    color: #2e3440 !important; /* Darker gray for description */
    font-weight: 700 !important;
    text-shadow: none !important;
}


/* Chart containers */
.chart-container {
    background: #f9f9f9;
    border-radius: 20px;
    padding: 30px;
    margin: 25px 0;
    box-shadow: 0 12px 35px rgba(15, 24, 39, 0.2);
    border: 2px solid rgba(255, 209, 89, 0.2);
}

/* Feedback form */
.feedback-form {
    background: linear-gradient(135deg, #f9f9f9 0%, #f0f0f0 100%);
    color: #222222; border-radius: 20px;
    padding: 30px;
    margin: 25px 0;
    box-shadow: 0 15px 40px rgba(255, 209, 89, 0.2);
    color: #1b263b;

}
/* Global section headers (subheadings) */
h2.section-header, h3.section-header, .section-header {
    color: #1b263b !important; /* Dark navy for clear headings */
    font-weight: 900 !important;
    text-shadow: none !important; /* Remove light shadows for sharpness */
}

/* Paragraphs and lists inside main content containers */
.main-container p,
.main-container ul,
.main-container li,
.article-card p,
.article-card li,
.feedback-form p,
.feedback-form label,
.export-container p,
.export-container li {
    color: #222222 !important; /* Dark charcoal for optimal readability */
    font-weight: 700 !important;
}

/* Specific container text color fixes */
.feedback-form,
.export-container,
.article-card {
    color: #222222 !important;
}

/* Remove any text shadows that reduce clarity inside white/light containers */
.main-container p, 
.article-card p,
.feedback-form p,
.export-container p {
    text-shadow: none !important;
}

/* Ensure link and interactive text colors are also dark enough */
a, a:hover, a:focus {
    color: #1b263b !important;
}

/* For better consistency, strong font weight for all titles/subtitles in containers */
.feedback-form h2,
.export-container h2,
.article-card h3 {
    color: #1b263b !important;
    font-weight: 900 !important;
}

/* For list bullets visibility */
.main-container ul {
    list-style-type: disc;
    margin-left: 20px;
}

</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'scripts', 'news_data.db')


def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_articles (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        published_at TIMESTAMP,
        source TEXT,
        processed INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_articles (
        id INTEGER PRIMARY KEY,
        raw_article_id INTEGER,
        title TEXT,
        sentiment_score REAL,
        sentiment_label TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(raw_article_id) REFERENCES raw_articles(id)
    )
    """)
    conn.commit()
    conn.close()


def get_db_connection():
    if not os.path.exists(DB_PATH):
        st.error(f"Database file not found at: {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=600)
def load_data():
    conn = get_db_connection()
    query = """
    SELECT pa.*, ra.published_at, ra.source, ra.description, ra.full_text
    FROM processed_articles pa 
    JOIN raw_articles ra ON pa.raw_article_id = ra.id
    ORDER BY pa.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if not df.empty:
        df['published_at'] = pd.to_datetime(df['published_at'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date
        df['hour'] = df['created_at'].dt.hour
    return df


def generate_wordcloud(text, title):
    stopwords = set(STOPWORDS)
    additional_stopwords = {'said', 'will', 'new', 'one', 'like', 'us', 'also', 'get'}
    stopwords.update(additional_stopwords)
    wordcloud = WordCloud(
        width=1200, height=600, background_color='white',
        stopwords=stopwords,
        colormap='Purples_r',
        max_words=150,
        contour_width=3,
        contour_color='#8a2be2',
        min_font_size=10,
        max_font_size=200
    ).generate(text)
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(title, fontsize=22, pad=30, fontweight='bold', color='#4b0082')
    plt.tight_layout()
    return fig


def send_feedback_email(name, email, feedback, rating):
    try:
        sender_email = st.secrets["email"]["user"]
        sender_password = st.secrets["email"]["password"]
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = "roserose9ish@gmail.com"
        msg['Subject'] = f"NewsPulse Feedback - Rating: {rating}/5"
        body = f"""
        Name: {name}
        Email: {email}
        Rating: {rating}/5
        Feedback:
        {feedback}
        """
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send feedback: {str(e)}")
        return False


def create_metric_card(value, label, help_text):
    return f"""
    <div class="metric-card" title="{help_text}">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def create_article_card(title, category, sentiment, score, source, published_at, description):
    sentiment_color = {
        'Positive': '#27ae60',
        'Negative': '#e74c3c',
        'Neutral': '#f39c12'
    }.get(sentiment, '#95a5a6')
    return f"""
    <div class="article-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #4b0082; font-weight: 700; flex: 1; font-size: 1.3rem; line-height: 1.4;">
                {title}
            </h3>
            <span style="background: {sentiment_color}; color: white; padding: 8px 18px; border-radius: 25px; 
                      font-weight: 700; font-size: 1rem; margin-left: 20px; min-width: 120px; text-align: center;">
                {sentiment} ({score:.2f})
            </span>
        </div>
        <p style="color: #b8860b; line-height: 1.6; margin-bottom: 15px; font-size: 1.1rem; font-weight: 700;">
            {description[:200]}...
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <span style="background: linear-gradient(135deg, #8a2be2 0%, #daa520 100%); color: white; 
                      padding: 6px 15px; border-radius: 20px; font-weight: 600; font-size: 0.9rem;">
                🏷️ {category}
            </span>
            <span style="color: #b8860b; font-size: 1rem; font-weight: 600;">
                📰 {source} • 📅 {published_at}
            </span>
        </div>
    </div>
    """


def main():
    # Centered, bold header with gradient text color
    st.markdown(
        "<h1 style='text-align: center; font-size: 4rem; font-weight: 900; "
        "background: linear-gradient(135deg, #f5deb3 0%, #daa520 100%); "
        "-webkit-background-clip: text; -webkit-text-fill-color: transparent; "
        "font-family: Inter, Segoe UI, sans-serif; letter-spacing: -1px; "
        "text-shadow: 3px 3px 6px rgba(255,255,255,0.3); margin-bottom: 1rem;'>"
        "📰 NEWSPULSE AI DASHBOARD</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='bold-paragraph' style='font-size:1.4rem; color:#f0e68c; text-align:center; "
        "text-shadow:2px 2px 4px rgba(0,0,0,0.3); margin-bottom:2rem;'>"
        "<strong>Enterprise-grade News Intelligence & Sentiment Analytics Platform</strong>"
        "</p>", unsafe_allow_html=True)

    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    df = load_data()
    if df.empty:
        st.warning("🚀 No data available. Run the pipeline to analyze news articles!")
        st.info("💡 Run: `python scripts/orchestrator.py` to start processing")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    with st.sidebar:
        st.markdown(
            "<div class='filter-section'><h3>🔍 FILTER CONTROLS</h3>"
            "<p>Refine your news analysis</p></div>",
            unsafe_allow_html=True
        )
        categories = ['All Categories'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("🏷️ SELECT CATEGORY", categories)
        sources = ['All Sources'] + sorted(df['source'].unique().tolist())
        selected_source = st.selectbox("📰 NEWS SOURCE", sources)
        sentiments = ['All Sentiments'] + sorted(df['sentiment_label'].unique().tolist())
        selected_sentiment = st.selectbox("😊 SENTIMENT", sentiments)
        st.markdown("---")
        st.markdown("**📅 DATE RANGE**")
        date_range = st.date_input(
            "",
            value=(df['date'].min(), df['date'].max()),
            label_visibility="collapsed"
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        st.markdown("---")
        st.markdown(f"""
        <div style='background: rgba(218, 165, 32, 0.1); padding: 20px; border-radius: 15px;'>
            <h4 style='margin:0; color: #4b0082;'>📈 LIVE STATISTICS</h4>
            <p>📊 Articles: <strong>{len(df)}</strong></p>
            <p>🏢 Sources: <strong>{df['source'].nunique()}</strong></p>
            <p>📅 Period: <strong>{df['date'].min()} to {df['date'].max()}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    if selected_category != 'All Categories':
        df = df[df['category'] == selected_category]
    if selected_source != 'All Sources':
        df = df[df['source'] == selected_source]
    if selected_sentiment != 'All Sentiments':
        df = df[df['sentiment_label'] == selected_sentiment]

    st.markdown("<h2 class='section-header'>📊 EXECUTIVE OVERVIEW</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card(f"{len(df):,}", "TOTAL ARTICLES", "Comprehensive news coverage"),
                    unsafe_allow_html=True)
    with col2:
        avg_sentiment = df['sentiment_score'].mean()
        st.markdown(create_metric_card(f"{avg_sentiment:.3f}", "AVG SENTIMENT", "Overall sentiment score (-1 to +1)"),
                    unsafe_allow_html=True)
    with col3:
        positive_count = len(df[df['sentiment_label'] == 'Positive'])
        st.markdown(create_metric_card(f"{positive_count}", "POSITIVE NEWS", "Articles with positive sentiment"),
                    unsafe_allow_html=True)
    with col4:
        dominant_category = df['category'].mode()[0] if not df['category'].mode().empty else "N/A"
        st.markdown(create_metric_card(dominant_category.upper(), "TOP CATEGORY", "Most frequent news category"),
                    unsafe_allow_html=True)
    st.divider()

    if not df.empty:
        st.markdown("<h2 class='section-header'>📰 LATEST NEWS ANALYSIS</h2>", unsafe_allow_html=True)
        articles_per_page = 4
        total_pages = max(1, (len(df) + articles_per_page - 1) // articles_per_page)
        page = st.number_input("📄 Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * articles_per_page
        end_idx = start_idx + articles_per_page
        paginated_df = df.iloc[start_idx:end_idx]
        for _, article in paginated_df.iterrows():
            st.markdown(create_article_card(
                article['title'],
                article['category'],
                article['sentiment_label'],
                article['sentiment_score'],
                article['source'],
                article['published_at'].strftime('%Y-%m-%d') if pd.notna(article['published_at']) else 'N/A',
                article['description'] or getattr(article, 'full_text', '') or 'No description available'
            ), unsafe_allow_html=True)
        st.divider()

    if not df.empty:
        st.markdown("<h2 class='section-header'>📈 ADVANCED ANALYTICS</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("### 🔤 TRENDING TOPICS ANALYSIS")
            all_titles = ' '.join(df['title'].dropna().astype(str))
            if all_titles.strip():
                wordcloud_fig = generate_wordcloud(all_titles, "Most Frequent Words in News Headlines")
                st.pyplot(wordcloud_fig)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("### 😊 SENTIMENT DISTRIBUTION")
            sentiment_counts = df['sentiment_label'].value_counts()
            if not sentiment_counts.empty:
                fig1 = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    color=sentiment_counts.index,
                    color_discrete_map={'Positive': '#27ae60', 'Negative': '#e74c3c', 'Neutral': '#f39c12'}
                )
                fig1.update_layout(
                    showlegend=True,
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=14, family='Inter')
                )
                st.plotly_chart(fig1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🏷️ CATEGORY BREAKDOWN")
            category_counts = df['category'].value_counts()
            if not category_counts.empty:
                fig2 = px.bar(
                    x=category_counts.values,
                    y=category_counts.index,
                    orientation='h',
                    color=category_counts.values,
                    color_continuous_scale='Purples',
                    labels={'x': 'Number of Articles', 'y': 'Category'}
                )
                fig2.update_layout(
                    showlegend=False,
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("### 📅 SENTIMENT TIMELINE")
            time_df = df.groupby('date').agg({
                'sentiment_score': 'mean',
                'id': 'count'
            }).reset_index()
            time_df.rename(columns={'id': 'article_count'}, inplace=True)
            if not time_df.empty:
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=time_df['date'],
                    y=time_df['sentiment_score'],
                    mode='lines+markers',
                    name='Avg Sentiment',
                    line=dict(color='#4b0082', width=4),
                    marker=dict(size=8, color='#daa520')
                ))
                fig3.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Sentiment Score',
                    hovermode='x unified',
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig3, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if not df.empty:
        st.divider()
        st.markdown("<h2 class='section-header'>💬 PROVIDE FEEDBACK</h2>", unsafe_allow_html=True)
        with st.form("feedback_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Your Name", placeholder="Enter your name")
                email = st.text_input("📧 Your Email", placeholder="your.email@example.com")
            with col2:
                rating = st.slider("⭐ Rating (1-5)", 1, 5, 5)
                feedback_type = st.selectbox("📋 Feedback Type",
                                             ["General Feedback", "Bug Report", "Feature Request", "Compliment"])
            feedback = st.text_area("💭 Your Feedback", placeholder="Share your thoughts...", height=150)
            submitted = st.form_submit_button("🚀 Submit Feedback", use_container_width=True)
            if submitted:
                if send_feedback_email(name, email, feedback, rating):
                    st.success("✅ Thank you for your feedback! We'll get back to you soon.")
                else:
                    st.warning("⚠️ Please configure email settings in the code")

    if not df.empty:
        st.divider()
        st.markdown("<h2 class='section-header'>📥 EXPORT DATA</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 DOWNLOAD DATASET",
                data=csv,
                file_name="news_analysis_export.csv",
                mime="text/csv",
                help="Download complete analyzed dataset",
                use_container_width=True
            )
        with col2:
            st.markdown(
                "<div style='background: linear-gradient(135deg, #fffaf0 0%, #fff5e1 100%); "
                "padding: 25px; border-radius: 18px;'>"
                "<h4 style='color: #4b0082; margin-bottom: 15px;'>📊 DATA EXPORT FEATURES</h4>"
                "<ul><li>Complete analyzed dataset in CSV format</li>"
                "<li>Includes sentiment scores, categories, and metadata</li>"
                "<li>Perfect for advanced analysis in Excel, Python, or R</li>"
                "<li>Ready for machine learning and statistical modeling</li></ul></div>", unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

