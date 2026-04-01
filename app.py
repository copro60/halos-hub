import streamlit as st
import streamlit.components.v1 as components
import statsapi
import requests
import pybaseball
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import date, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Halos Hub", layout="wide", page_icon="⚾")

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
/* ── Base ── */
.stApp {
    background-color: #080B10;
    color: #E8ECF0;
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── Typography ── */
h1, h2, h3, .section-title {
    font-family: 'Barlow Condensed', sans-serif;
    letter-spacing: 0.03em;
}

/* ── App Header ── */
.hub-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 18px 24px;
    background: linear-gradient(135deg, #0D1117 0%, #12181F 60%, #1a0308 100%);
    border: 1px solid #1E2530;
    border-left: 4px solid #BA0021;
    border-radius: 10px;
    margin-bottom: 20px;
}
.hub-header img { width: 64px; }
.hub-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #FFFFFF;
    line-height: 1;
    margin: 0;
}
.hub-subtitle {
    font-size: 0.75rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 4px;
    font-weight: 500;
}
.hub-badge {
    margin-left: auto;
    background: #BA0021;
    color: white;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 4px 12px;
    border-radius: 20px;
    text-transform: uppercase;
}

/* ── Section Card ── */
.card {
    background: #0D1117;
    border: 1px solid #1E2530;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.section-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #BA0021;
    margin-bottom: 4px;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 16px 0;
}

/* ── Scoreboard Tile ── */
.score-tile {
    background: #0D1117;
    border: 1px solid #1E2530;
    border-radius: 8px;
    padding: 12px 14px;
    text-align: center;
    height: 100%;
}
.score-tile .teams {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    color: #9CA3AF;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.score-tile .score {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.1;
    margin: 4px 0;
}
.score-tile .status-live {
    display: inline-block;
    background: #BA0021;
    color: white;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 3px;
}
.score-tile .status-other {
    font-size: 0.68rem;
    color: #6B7280;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Hero Scoreboard (Angels game) ── */
.hero-team {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.hero-runs {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1;
}
.hero-vs {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.2rem;
    font-weight: 600;
    color: #374151;
    text-align: center;
    padding-top: 30px;
}
.hero-status {
    background: #BA0021;
    color: white;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 8px;
}
.hero-meta {
    font-size: 0.78rem;
    color: #6B7280;
    margin-top: 12px;
    border-top: 1px solid #1E2530;
    padding-top: 12px;
}

/* ── News Card ── */
.news-item {
    border-bottom: 1px solid #1E2530;
    padding: 12px 0;
}
.news-item:last-child { border-bottom: none; }
.news-title {
    font-size: 0.88rem;
    font-weight: 500;
    color: #E8ECF0;
    line-height: 1.4;
    text-decoration: none;
    display: block;
    margin-bottom: 5px;
}
.news-title:hover { color: #BA0021; }
.news-meta {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.source-badge {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 3px;
    display: inline-block;
}
.badge-reddit  { background: #2a1a0a; color: #FF4500; border: 1px solid #3d2510; }
.badge-mlb     { background: #001a33; color: #0085CA; border: 1px solid #00264d; }
.badge-espn    { background: #1a0a00; color: #FF6600; border: 1px solid #2e1500; }

/* ── Standings ── */
.standings-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #1E2530;
    font-size: 0.85rem;
}
.standings-row:last-child { border-bottom: none; }
.standings-row .team-name { font-weight: 500; color: #E8ECF0; }
.standings-row .team-name.angels { color: #BA0021; font-weight: 700; }
.standings-row .record { color: #9CA3AF; font-family: 'Barlow Condensed', sans-serif; font-size: 1rem; }
.standings-row .gb { color: #6B7280; font-size: 0.8rem; width: 30px; text-align: right; }

/* ── DataFrames ── */
.stDataFrame { border: none !important; }
[data-testid="stDataFrame"] { border: 1px solid #1E2530; border-radius: 8px; overflow: hidden; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1E2530;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6B7280 !important;
    padding: 8px 20px;
    border-radius: 0;
}
.stTabs [aria-selected="true"] {
    color: #BA0021 !important;
    border-bottom: 2px solid #BA0021 !important;
    background: transparent;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0D1117;
    border: 1px solid #1E2530 !important;
    border-radius: 8px;
}

/* ── Cheat sheet ── */
.stat-term {
    color: #BA0021;
    font-weight: 600;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    letter-spacing: 0.04em;
}
.stat-def { color: #9CA3AF; font-size: 0.82rem; margin-bottom: 10px; }

/* ── Divider ── */
hr { border-color: #1E2530 !important; margin: 16px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
ANGELS_ID = 108

# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
def get_standings_table():
    try:
        data = statsapi.standings_data(leagueId=103, division="alw")[200]['teams']
        df = pd.DataFrame(data)[['name', 'w', 'l', 'gb']]
        df.columns = ['Team', 'W', 'L', 'GB']
        return df
    except:
        return pd.DataFrame()

def get_reddit_news(sub="angelsbaseball", limit=8):
    url = f"https://www.reddit.com/r/{sub}/hot.json?limit={limit+3}"
    headers = {'User-agent': 'HalosHub 3.0'}
    try:
        res = requests.get(url, headers=headers).json()
        posts = [p['data'] for p in res['data']['children'] if not p['data']['stickied']][:limit]
        return [{'title': p['title'], 'url': f"https://www.reddit.com{p['permalink']}",
                 'meta': f"👍 {p['ups']:,}  ·  u/{p['author']}", 'source': 'reddit'} for p in posts]
    except:
        return []

def get_rss_news(url, source_key, limit=6):
    try:
        res = requests.get(url, headers={'User-Agent': 'HalosHub 3.0'}, timeout=5)
        root = ET.fromstring(res.content)
        items = root.findall('.//item')[:limit]
        results = []
        for item in items:
            title = item.findtext('title', '').strip()
            link  = item.findtext('link', '').strip()
            pub   = item.findtext('pubDate', '')[:16] if item.findtext('pubDate') else ''
            if title and link:
                results.append({'title': title, 'url': link, 'meta': pub, 'source': source_key})
        return results
    except:
        return []

def get_all_news():
    reddit = get_reddit_news(limit=8)
    mlb    = get_rss_news('https://www.mlb.com/angels/feeds/news/rss.xml', 'mlb', limit=6)
    espn   = get_rss_news('https://www.espn.com/espn/rss/mlb/news', 'espn', limit=6)
    return {'Reddit': reddit, 'MLB.com': mlb, 'ESPN': espn}

@st.cache_data(ttl=3600)
def get_advanced_stats(stat_type="batting"):
    try:
        if stat_type == "batting":
            df = pybaseball.batting_stats(2026, qual=5)
            cols = ['Name', 'AVG', 'wRC+', 'OPS', 'HardHit%']
        else:
            df = pybaseball.pitching_stats(2026, qual=1)
            cols = ['Name', 'ERA', 'WHIP', 'K/9', 'FIP']
        return df[df['Team'] == 'LAA'][cols]
    except:
        return pd.DataFrame()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hub-header">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Los_Angeles_Angels_of_Anaheim.svg/200px-Los_Angeles_Angels_of_Anaheim.svg.png"/>
    <div>
        <div class="hub-title">Halos Hub</div>
        <div class="hub-subtitle">Los Angeles Angels · Live Data Feed</div>
    </div>
    <div class="hub-badge">{date.today().strftime('%b %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LEAGUE SCOREBOARD
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Around the Majors</div><div class="section-title" style="margin-bottom:12px;">League Scoreboard</div>', unsafe_allow_html=True)

try:
    mlb_games = statsapi.schedule(date=date.today())
    cols = st.columns(6)
    for i, g in enumerate(mlb_games[:6]):
        is_live = g['status'] == "In Progress"
        away_abbr = g['away_name'].split()[-1].upper()
        home_abbr = g['home_name'].split()[-1].upper()
        status_html = (
            '<span class="status-live">● Live</span>'
            if is_live
            else f'<span class="status-other">{g["status"]}</span>'
        )
        with cols[i]:
            st.markdown(f"""
            <div class="score-tile">
                <div class="teams">{away_abbr} @ {home_abbr}</div>
                <div class="score">{g.get('away_score', 0)} – {g.get('home_score', 0)}</div>
                {status_html}
            </div>
            """, unsafe_allow_html=True)
except:
    st.info("Scoreboard loading…")

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN + SIDEBAR LAYOUT
# ─────────────────────────────────────────────
col_main, col_side = st.columns([7, 3], gap="large")

# ── LEFT: MAIN ──
with col_main:

    # GAME CENTER
    st.markdown('<div class="section-label">Game Center</div><div class="section-title">Angels Game</div>', unsafe_allow_html=True)
    try:
        sched = statsapi.schedule(
            team=ANGELS_ID,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today()
        )
        game = next((g for g in sched if g['status'] == 'In Progress'), sched[-1])

        is_live = game['status'] == 'In Progress'
        g_cols = st.columns([5, 1, 5])

        with g_cols[0]:
            st.markdown(f"""
            <div>
                <div class="hero-team">{game['away_name']}</div>
                <div class="hero-runs">{game.get('away_score', '–')}</div>
            </div>
            """, unsafe_allow_html=True)
        with g_cols[1]:
            st.markdown('<div class="hero-vs">VS</div>', unsafe_allow_html=True)
        with g_cols[2]:
            st.markdown(f"""
            <div>
                <div class="hero-team">{game['home_name']}</div>
                <div class="hero-runs">{game.get('home_score', '–')}</div>
            </div>
            """, unsafe_allow_html=True)

        status_badge = f'<span class="hero-status">{"● Live" if is_live else game["status"]}</span>'
        st.markdown(f"""
        {status_badge}
        <div class="hero-meta">
            ⚾ &nbsp;<b>Probables:</b>&nbsp;
            {game.get('away_probable_pitcher', 'TBD')} vs {game.get('home_probable_pitcher', 'TBD')}
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View Full Line Score"):
            ls_data = statsapi.linescore(game['game_id'])
            st.code(ls_data, language=None)

    except:
        st.warning("No active Angels game data found for today.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # STATS TABLES
    st.markdown('<div class="section-label">Fangraphs · 2026</div><div class="section-title">Team Performance</div>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["Batting Leaders", "Pitching Leaders"])
    with t1:
        df_bat = get_advanced_stats("batting")
        if not df_bat.empty:
            st.dataframe(
                df_bat.sort_values("wRC+", ascending=False).reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Batting stats loading…")
    with t2:
        df_pit = get_advanced_stats("pitching")
        if not df_pit.empty:
            st.dataframe(
                df_pit.sort_values("ERA").reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Pitching stats loading…")

# ── RIGHT: SIDEBAR ──
with col_side:

    # STANDINGS
    st.markdown('<div class="section-label">AL West</div><div class="section-title">Standings</div>', unsafe_allow_html=True)
    standings_df = get_standings_table()
    if not standings_df.empty:
        rows_html = ""
        for _, row in standings_df.iterrows():
            is_angels = "Angels" in row['Team']
            name_color = "#BA0021" if is_angels else "#E8ECF0"
            name_weight = "700" if is_angels else "500"
            gb_display = "—" if str(row['GB']) in ("0", "0.0", "") else row['GB']
            rows_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:9px 0;border-bottom:1px solid #1E2530;font-size:0.85rem;">
                <span style="color:{name_color};font-weight:{name_weight};font-family:'Inter',sans-serif;">{row['Team']}</span>
                <span style="color:#9CA3AF;font-family:'Barlow Condensed',sans-serif;font-size:1rem;letter-spacing:0.03em;">{row['W']}–{row['L']}</span>
                <span style="color:#6B7280;font-size:0.8rem;width:30px;text-align:right;">{gb_display}</span>
            </div>
            """
        standings_html = f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-radius:10px;padding:16px 20px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;
                        font-size:0.65rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#6B7280;">
                <span>Team</span><span>W–L</span><span>GB</span>
            </div>
            {rows_html}
        </div>
        """
        components.html(standings_html, height=len(standings_df) * 44 + 80, scrolling=False)
    else:
        st.info("Standings loading…")

    st.markdown("<hr>", unsafe_allow_html=True)

    # NEWS FEED
    st.markdown('<div class="section-label">Latest Coverage</div><div class="section-title">Halos Headlines</div>', unsafe_allow_html=True)

    BADGE_STYLES = {
        'reddit': ('Reddit',  '#FF4500', '#2a1a0a', '#3d2510'),
        'mlb':    ('MLB.com', '#0085CA', '#001a33', '#00264d'),
        'espn':   ('ESPN',    '#FF6600', '#1a0a00', '#2e1500'),
    }

    all_news = get_all_news()
    tab_labels = list(all_news.keys())

    news_tabs = st.tabs(tab_labels)
    for tab, label in zip(news_tabs, tab_labels):
        source_key = {'Reddit': 'reddit', 'MLB.com': 'mlb', 'ESPN': 'espn'}[label]
        posts = all_news[label]
        with tab:
            if posts:
                items_html = ""
                for item in posts:
                    lbl, color, bg, border = BADGE_STYLES[item['source']]
                    badge = (f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:0.62rem;'
                             f'font-weight:700;letter-spacing:0.12em;text-transform:uppercase;'
                             f'padding:2px 7px;border-radius:3px;background:{bg};color:{color};'
                             f'border:1px solid {border};display:inline-block;">{lbl}</span>')
                    items_html += f"""
                    <div style="border-bottom:1px solid #1E2530;padding:12px 0;">
                        <a href="{item['url']}" target="_blank"
                           style="font-family:'Inter',sans-serif;font-size:0.88rem;font-weight:500;
                                  color:#E8ECF0;line-height:1.4;text-decoration:none;display:block;margin-bottom:6px;">
                            {item['title']}
                        </a>
                        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                            {badge}
                            <span style="font-size:0.72rem;color:#6B7280;">{item['meta']}</span>
                        </div>
                    </div>
                    """
                full_html = f"""
                <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
                <div style="background:#0D1117;border:1px solid #1E2530;border-radius:10px;padding:12px 20px;">
                    {items_html}
                </div>
                """
                components.html(full_html, height=len(posts) * 78 + 30, scrolling=False)
            else:
                st.info(f"No {label} stories available right now.")

# ─────────────────────────────────────────────
# DID YOU KNOW — Fun Facts Card
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Did You Know?</div><div class="section-title" style="margin-bottom:4px;">⚡ Halos & Baseball Facts</div>', unsafe_allow_html=True)

# Facts rotate daily — index by day of year so it changes every day automatically
FUN_FACTS = [
    ("🎯", "Zach Neto's Cannon Arm", "#0085CA",
     "Zach Neto posted one of the highest arm-strength grades among all MLB shortstops in 2024, regularly hitting throws of 95+ mph. He's built like a quarterback playing shortstop."),
    ("🔥", "The Rally Monkey Origin", "#BA0021",
     "The Rally Monkey was born on June 6, 2000 when a stadium video operator played a clip from the movie 'Ace Ventura' during a late-inning comeback. It became one of baseball's most iconic traditions."),
    ("⚡", "Mike Trout's All-Time WAR Pace", "#FFD700",
     "Mike Trout accumulated more career WAR (Wins Above Replacement) by age 26 than any player in MLB history — including Willie Mays and Mickey Mantle. He did it in a small market with zero playoff wins."),
    ("🌊", "The Big A Halo Tradition", "#22c55e",
     "The giant halo atop Angel Stadium lights up red after every Angels home win. It's been doing it since 1966 and is one of the most recognized landmarks in all of Anaheim."),
    ("🎲", "Baseball's Weird Math", "#9CA3AF",
     "A .300 batting average is considered excellent — but it means the hitter fails 70% of the time. No other major sport celebrates failure at that rate as a sign of greatness."),
    ("💥", "Exit Velocity is Everything", "#FF6600",
     "A ball hit at 95 mph has roughly a 30% chance of being a hit. At 100+ mph? Over 50%. At 110 mph it's nearly automatic. The Angels track this obsessively in player development."),
    ("🏟️", "Angel Stadium's Age", "#0085CA",
     "Angel Stadium opened in 1966, making it the third-oldest ballpark in the American League. Only Fenway Park (1912) and Wrigley Field (1914) are older among active MLB parks."),
    ("🧢", "Nolan Ryan's Angels Years", "#BA0021",
     "Nolan Ryan pitched for the Angels from 1972–1979 and threw 4 of his 7 no-hitters in Anaheim. He also struck out a then-record 383 batters in a single season (1973) as an Angel."),
    ("📐", "The Shift is Gone", "#22c55e",
     "MLB banned the defensive shift before the 2023 season, requiring two infielders on each side of second base. Batting averages league-wide jumped nearly 10 points the first year — exactly as predicted."),
    ("🎯", "Pitch Framing is Worth Wins", "#FFD700",
     "Pitch framing — how a catcher presents a pitch to steal borderline strikes — is worth up to 2–3 wins per year for an elite backstop. It's one of the most underrated skills in baseball."),
    ("🚀", "High Spin = Rising Fastball", "#FF6600",
     "A four-seam fastball with high spin rate (2,400+ RPM) appears to 'rise' because it drops less than the hitter's brain expects. It's an optical illusion baked into physics."),
    ("💡", "Why Stolen Bases Came Back", "#0085CA",
     "After years of decline, stolen bases surged in 2023 after MLB increased base sizes by 3 inches and limited pickoff attempts. Speed became a weapon again overnight."),
    ("🏆", "2002: The Greatest Comeback", "#BA0021",
     "The Angels trailed the Giants 3-2 in games and were down 3 runs with 8 outs left in Game 6. They tied it, won in extras, then took Game 7 the next night. Still the only title in franchise history."),
    ("🧠", "WAR Explained Simply", "#9CA3AF",
     "WAR (Wins Above Replacement) asks: how many wins did this player add vs a replacement-level minor leaguer? 2 WAR = solid starter. 5+ = All-Star. 8+ = MVP candidate. Trout once posted a 10.5."),
    ("🎵", "Gene Autry's Wild Bet", "#22c55e",
     "Gene Autry only wanted an LA radio broadcast license. MLB said he had to buy a team to get it. He paid $2.1M for the Angels in 1961. The franchise is now worth over $2 billion."),
]

# Pick 3 facts rotating daily
day_idx = date.today().timetuple().tm_yday
fact_cols = st.columns(3)
for col_i, col in enumerate(fact_cols):
    fact = FUN_FACTS[(day_idx + col_i) % len(FUN_FACTS)]
    icon, label, color, text = fact
    with col:
        fact_html = f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-top:3px solid {color};
                    border-radius:10px;padding:18px 20px;height:100%;box-sizing:border-box;">
            <div style="font-size:1.8rem;margin-bottom:8px;">{icon}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;font-weight:700;
                        letter-spacing:0.2em;text-transform:uppercase;color:{color};margin-bottom:6px;">{label}</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.84rem;color:#C9D1D9;line-height:1.6;">{text}</div>
        </div>
        """
        components.html(fact_html, height=210, scrolling=False)

# ─────────────────────────────────────────────
# MLB NEWS — Around the League
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Around the Majors</div><div class="section-title" style="margin-bottom:4px;">📰 MLB News</div>', unsafe_allow_html=True)

@st.cache_data(ttl=1800)
def get_mlb_general_news():
    feeds = [
        ("https://www.mlb.com/feeds/news/rss.xml",       "mlb",  "MLB.com"),
        ("https://www.espn.com/espn/rss/mlb/news",        "espn", "ESPN"),
        ("https://feeds.nbcsports.com/nbcsports/rss/mlb", "nbc",  "NBC Sports"),
    ]
    BADGE_STYLES = {
        'mlb':  ('#0085CA', '#001a33', '#00264d'),
        'espn': ('#FF6600', '#1a0a00', '#2e1500'),
        'nbc':  ('#E03A3E', '#1a0003', '#2e0006'),
    }
    all_items = []
    for url, key, name in feeds:
        try:
            res = requests.get(url, headers={'User-Agent': 'HalosHub 3.0'}, timeout=5)
            root = ET.fromstring(res.content)
            for item in root.findall('.//item')[:8]:
                title = item.findtext('title', '').strip()
                link  = item.findtext('link',  '').strip()
                pub   = item.findtext('pubDate', '')[:16] if item.findtext('pubDate') else ''
                if title and link:
                    all_items.append({'title': title, 'url': link, 'pub': pub,
                                      'source': name, 'key': key})
        except:
            pass
    return all_items, BADGE_STYLES

mlb_news, BADGE_STYLES = get_mlb_general_news()

if mlb_news:
    left_col, right_col = st.columns(2)
    for i, item in enumerate(mlb_news[:16]):
        col = left_col if i % 2 == 0 else right_col
        color, bg, border = BADGE_STYLES[item['key']]
        badge = (f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:0.6rem;font-weight:700;'                 f'letter-spacing:0.12em;text-transform:uppercase;padding:2px 7px;border-radius:3px;'                 f'background:{bg};color:{color};border:1px solid {border};display:inline-block;">{item["source"]}</span>')
        card_html = f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-radius:8px;padding:14px 16px;margin-bottom:2px;">
            <a href="{item['url']}" target="_blank"
               style="font-family:'Inter',sans-serif;font-size:0.87rem;font-weight:500;
                      color:#E8ECF0;line-height:1.45;text-decoration:none;display:block;margin-bottom:8px;">
                {item['title']}
            </a>
            <div style="display:flex;align-items:center;gap:8px;">
                {badge}
                <span style="font-size:0.7rem;color:#6B7280;">{item['pub']}</span>
            </div>
        </div>
        """
        with col:
            components.html(card_html, height=115, scrolling=False)
else:
    st.info("MLB news loading…")


st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("🎓  Water Cooler Cheat Sheet — Sound Smart Today"):
    left, right = st.columns(2)
    with left:
        st.markdown("""
        <div class="section-label">Hitting</div>
        <p><span class="stat-term">wRC+</span><br>
        <span class="stat-def">Weighted Runs Created Plus. 100 is league average; 150 is elite. Best single-number hitting metric.</span></p>
        <p><span class="stat-term">HardHit%</span><br>
        <span class="stat-def">Balls hit over 95 mph. High % = consistent quality contact, not just lucky singles.</span></p>
        <p><span class="stat-term">OPS</span><br>
        <span class="stat-def">On-base + Slugging. Over .850 is very good. Simple but noisy.</span></p>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("""
        <div class="section-label">Pitching</div>
        <p><span class="stat-term">FIP</span><br>
        <span class="stat-def">Fielding Independent Pitching. ERA without the luck — only counts Ks, BBs, HRs. True skill indicator.</span></p>
        <p><span class="stat-term">WHIP</span><br>
        <span class="stat-def">Walks + Hits per inning. Under 1.10 is ace territory. Under 1.00 is Cy Young material.</span></p>
        <p><span class="stat-term">K/9</span><br>
        <span class="stat-def">Strikeouts per 9 innings. 10+ is electric stuff. Shows pure dominance.</span></p>
        """, unsafe_allow_html=True)