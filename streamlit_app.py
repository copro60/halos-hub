import streamlit as st
import streamlit.components.v1 as components
import statsapi
import requests
import pybaseball
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
import zoneinfo

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Halos Hub", layout="wide", page_icon="⚾")

# ─────────────────────────────────────────────
# GLOBAL STYLES — injected via components.html
# to bypass Streamlit's HTML sanitizer
# ─────────────────────────────────────────────
components.html("""
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #080B10 !important; color: #E8ECF0; font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.03em; }

    .hub-header {
        display: flex; align-items: center; gap: 18px; padding: 18px 24px;
        background: linear-gradient(135deg, #0D1117 0%, #12181F 60%, #1a0308 100%);
        border: 1px solid #1E2530; border-left: 4px solid #BA0021;
        border-radius: 10px; margin-bottom: 20px;
    }
    .hub-header img { width: 64px; }
    .hub-title {
        font-family: 'Barlow Condensed', sans-serif; font-size: 2.4rem;
        font-weight: 800; letter-spacing: 0.04em; color: #FFFFFF; line-height: 1; margin: 0;
    }
    .hub-subtitle {
        font-size: 0.75rem; color: #6B7280; text-transform: uppercase;
        letter-spacing: 0.12em; margin-top: 4px; font-weight: 500;
    }
    .hub-badge {
        margin-left: auto; background: #BA0021; color: white;
        font-family: 'Barlow Condensed', sans-serif; font-size: 0.8rem;
        font-weight: 700; letter-spacing: 0.1em; padding: 4px 12px;
        border-radius: 20px; text-transform: uppercase;
    }
    .section-label {
        font-family: 'Barlow Condensed', sans-serif; font-size: 0.65rem;
        font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase;
        color: #BA0021; margin-bottom: 4px;
    }
    .section-title { font-size: 1.4rem; font-weight: 700; color: #FFFFFF; margin: 0 0 16px 0; }

    .score-tile {
        background: #0D1117; border: 1px solid #1E2530; border-radius: 8px;
        padding: 12px 14px; text-align: center; height: 100%;
    }
    .score-tile .teams {
        font-family: 'Barlow Condensed', sans-serif; font-size: 0.8rem; font-weight: 600;
        color: #9CA3AF; letter-spacing: 0.06em; text-transform: uppercase;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .score-tile .score {
        font-family: 'Barlow Condensed', sans-serif; font-size: 1.8rem;
        font-weight: 800; color: #FFFFFF; line-height: 1.1; margin: 4px 0;
    }
    .score-tile .status-live {
        display: inline-block; background: #BA0021; color: white; font-size: 0.6rem;
        font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase;
        padding: 2px 8px; border-radius: 3px;
    }
    .score-tile .status-other {
        font-size: 0.68rem; color: #6B7280; letter-spacing: 0.08em; text-transform: uppercase;
    }
    .hero-team {
        font-family: 'Barlow Condensed', sans-serif; font-size: 1.5rem; font-weight: 700;
        color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;
    }
    .hero-runs {
        font-family: 'Barlow Condensed', sans-serif; font-size: 4rem;
        font-weight: 800; color: #FFFFFF; line-height: 1;
    }
    .hero-vs {
        font-family: 'Barlow Condensed', sans-serif; font-size: 1.2rem;
        font-weight: 600; color: #374151; text-align: center; padding-top: 30px;
    }
    .hero-status {
        background: #BA0021; color: white; font-family: 'Barlow Condensed', sans-serif;
        font-size: 0.8rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
        padding: 5px 14px; border-radius: 4px; display: inline-block; margin-bottom: 8px;
    }
    .hero-meta {
        font-size: 0.78rem; color: #6B7280; margin-top: 12px;
        border-top: 1px solid #1E2530; padding-top: 12px;
    }
    .stDataFrame { border: none !important; }
    [data-testid="stDataFrame"] { border: 1px solid #1E2530; border-radius: 8px; overflow: hidden; }
    .stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid #1E2530; gap: 0; }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Barlow Condensed', sans-serif; font-size: 0.9rem; font-weight: 600;
        letter-spacing: 0.08em; text-transform: uppercase; color: #6B7280 !important;
        padding: 8px 20px; border-radius: 0;
    }
    .stTabs [aria-selected="true"] {
        color: #BA0021 !important; border-bottom: 2px solid #BA0021 !important; background: transparent;
    }
    [data-testid="stExpander"] { background: #0D1117; border: 1px solid #1E2530 !important; border-radius: 8px; }
    .stat-term {
        color: #BA0021; font-weight: 600; font-family: 'Barlow Condensed', sans-serif;
        font-size: 1rem; letter-spacing: 0.04em;
    }
    .stat-def { color: #9CA3AF; font-size: 0.82rem; margin-bottom: 10px; }
    hr { border-color: #1E2530 !important; margin: 16px 0 !important; }
</style>
<script>
    // Push styles into the parent Streamlit document
    const styles = document.querySelector('style');
    const link   = document.querySelector('link');
    if (styles) window.parent.document.head.appendChild(styles.cloneNode(true));
    if (link)   window.parent.document.head.appendChild(link.cloneNode(true));
</script>
""", height=0)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
ANGELS_ID = 108
PT = pytz.timezone('America/Los_Angeles')

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

def get_rss_news(url, source_key, limit=6):
    try:
        res = requests.get(url, headers={'User-Agent': 'HalosHub 3.0'}, timeout=5)
        root = ET.fromstring(res.content)
        results = []
        for item in root.findall('.//item')[:limit]:
            title = item.findtext('title', '').strip()
            link  = item.findtext('link', '').strip()
            pub   = item.findtext('pubDate', '')[:16] if item.findtext('pubDate') else ''
            if title and link:
                results.append({'title': title, 'url': link, 'meta': pub, 'source': source_key})
        return results
    except:
        return []

def get_all_news():
    mlb  = get_rss_news('https://www.mlb.com/angels/feeds/news/rss.xml', 'mlb', limit=8)
    espn = get_rss_news('https://www.espn.com/espn/rss/mlb/news', 'espn', limit=8)
    return {'MLB.com': mlb, 'ESPN': espn}

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
                    all_items.append({'title': title, 'url': link, 'pub': pub, 'source': name, 'key': key})
        except:
            pass
    return all_items, BADGE_STYLES

def get_schedule_strip():
    try:
        end = date.today() + timedelta(days=7)
        games = statsapi.schedule(team=ANGELS_ID, start_date=date.today(), end_date=end)
        return games[:8]
    except:
        return []

def get_injury_report():
    try:
        roster = statsapi.roster(ANGELS_ID, rosterType='injuries')
        lines = [l.strip() for l in roster.strip().split('\n') if l.strip()]
        return lines[:10]
    except:
        return []

def get_anaheim_weather():
    try:
        res = requests.get(
            "https://wttr.in/Anaheim,CA?format=j1",
            headers={'User-Agent': 'HalosHub 3.0'}, timeout=5
        ).json()
        cur = res['current_condition'][0]
        desc = cur['weatherDesc'][0]['value']
        temp_f = cur['temp_F']
        feels_f = cur['FeelsLikeF']
        humidity = cur['humidity']
        wind_mph = cur['windspeedMiles']
        return {'desc': desc, 'temp': temp_f, 'feels': feels_f,
                'humidity': humidity, 'wind': wind_mph}
    except:
        return None

def parse_game_time(raw):
    try:
        gt = datetime.fromisoformat(raw.replace('Z', '+00:00')).astimezone(PT)
        return gt.strftime('%-I:%M %p PT'), gt.strftime('%a %b %-d')
    except:
        return '', ''

# Player spotlight — rotates daily
SPOTLIGHTS = [
    {"name": "Zach Neto", "pos": "SS", "emoji": "🔥",
     "stats": "Emerging as one of the AL's best young shortstops with elite arm strength and improving contact rates.",
     "fun": "His throws to first base regularly clock at 95+ mph — stronger than most outfield arms."},
    {"name": "Mike Trout", "pos": "CF", "emoji": "⭐",
     "stats": "The greatest Angel ever. Accumulated more WAR by age 26 than any player in MLB history.",
     "fun": "Trout has never played in a World Series despite being the best player of his generation."},
    {"name": "Tyler Anderson", "pos": "SP", "emoji": "⚾",
     "stats": "Veteran left-hander known for command and changing speeds. A steady presence at the top of the rotation.",
     "fun": "Anderson has faced over 4,000 major league batters and still relies on a mid-80s changeup as his strikeout pitch."},
    {"name": "Logan O'Hoppe", "pos": "C", "emoji": "🎯",
     "stats": "One of the best young catchers in baseball, O'Hoppe combines elite framing with surprising pop at the plate.",
     "fun": "He was traded from the Phillies in the Noah Syndergaard deal — already looking like a massive Angels win."},
    {"name": "Reid Detmers", "pos": "SP", "emoji": "💫",
     "stats": "Power left-hander with a devastating slider and the stuff to be a true ace. Strikeout rates rival the AL's best.",
     "fun": "Detmers threw a no-hitter in just his 11th career MLB start — one of the fastest ever."},
    {"name": "Anthony Rendon", "pos": "3B", "emoji": "💪",
     "stats": "When healthy, one of the most complete hitters in the game. Contact, power, and plate discipline in one package.",
     "fun": "Rendon hit .319 and drove in 126 runs for Washington in 2019, finishing 2nd in NL MVP voting."},
    {"name": "Luis Rengifo", "pos": "2B/SS", "emoji": "⚡",
     "stats": "Versatile infielder with sneaky pop and above-average speed. A steady glue piece in the Angels lineup.",
     "fun": "Rengifo can play every infield position and has even seen time in the outfield in a pinch."},
]

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
        status_html = ('<span class="status-live">● Live</span>' if is_live
                       else f'<span class="status-other">{g["status"]}</span>')
        with cols[i]:
            st.markdown(f"""
            <div class="score-tile">
                <div class="teams">{away_abbr} @ {home_abbr}</div>
                <div class="score">{g.get('away_score', 0)} – {g.get('home_score', 0)}</div>
                {status_html}
            </div>""", unsafe_allow_html=True)
except:
    st.info("Scoreboard loading…")

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN + SIDEBAR
# ─────────────────────────────────────────────
col_main, col_side = st.columns([7, 3], gap="large")

# ══════════════════════════════════════════════
# LEFT: MAIN
# ══════════════════════════════════════════════
with col_main:

    # ── GAME CENTER ──
    st.markdown('<div class="section-label">Game Center</div><div class="section-title">Angels Game</div>', unsafe_allow_html=True)
    try:
        sched = statsapi.schedule(
            team=ANGELS_ID,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today()
        )
        game = next((g for g in sched if g['status'] == 'In Progress'), sched[-1])
        is_live   = game['status'] == 'In Progress'
        is_future = game['status'] in ('Preview', 'Pre-Game', 'Scheduled', 'Warmup')

        raw_time = game.get('game_datetime', '')
        game_time_str, game_date_str = parse_game_time(raw_time)
        venue   = game.get('venue_name', 'TBD')
        away_sp = game.get('away_probable_pitcher', 'TBD')
        home_sp = game.get('home_probable_pitcher', 'TBD')
        away_score = game.get('away_score', '–') if not is_future else '–'
        home_score = game.get('home_score', '–') if not is_future else '–'
        status_label = "● LIVE" if is_live else game['status'].upper()
        status_bg    = "#BA0021" if is_live else "#1E2530"
        status_color = "#FFFFFF" if is_live else "#9CA3AF"

        # Win probability block
        wp_html = ""
        if is_live:
            try:
                away_r = int(game.get('away_score', 0) or 0)
                home_r = int(game.get('home_score', 0) or 0)
                gd = statsapi.get('game', {'gamePk': game['game_id']})
                linescore   = gd.get('liveData', {}).get('linescore', {})
                inning      = linescore.get('currentInning', '?')
                inning_half = linescore.get('inningHalf', '')
                diff        = home_r - away_r
                home_pct    = min(max(50 + diff * 8, 5), 95)
                away_pct    = 100 - home_pct
                angels_home = game['home_name'] == 'Los Angeles Angels'
                angels_pct  = home_pct if angels_home else away_pct
                opp_pct     = 100 - angels_pct
                bar_color   = "#BA0021" if angels_pct >= 50 else "#374151"
                wp_html = f"""
                <div style="margin-top:16px;border-top:1px solid #1E2530;padding-top:14px;">
                    <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.18em;
                                text-transform:uppercase;color:#6B7280;margin-bottom:8px;">
                        Win Probability · {inning_half} {inning}
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.95rem;
                                font-weight:700;margin-bottom:6px;">
                        <span style="color:#BA0021;">Angels {angels_pct:.0f}%</span>
                        <span style="color:#6B7280;">Opp {opp_pct:.0f}%</span>
                    </div>
                    <div style="background:#1E2530;border-radius:4px;height:8px;overflow:hidden;">
                        <div style="background:{bar_color};width:{angels_pct:.0f}%;height:100%;border-radius:4px;"></div>
                    </div>
                </div>"""
            except:
                pass

        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:linear-gradient(160deg,#0D1117 0%,#110308 100%);
                    border:1px solid #2a0a12;border-radius:12px;padding:24px 28px;">

            <!-- Status pill + meta -->
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;flex-wrap:wrap;">
                <span style="background:{status_bg};color:{status_color};font-family:'Barlow Condensed',sans-serif;
                             font-size:0.7rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
                             padding:4px 12px;border-radius:4px;">{status_label}</span>
                <span style="font-size:0.78rem;color:#6B7280;">🕐 <b style="color:#9CA3AF;">{game_time_str}{f"  ·  {game_date_str}" if game_date_str else ""}</b></span>
                <span style="font-size:0.78rem;color:#6B7280;">🏟️ <b style="color:#9CA3AF;">{venue}</b></span>
            </div>

            <!-- Scoreboard row -->
            <div style="display:grid;grid-template-columns:1fr 60px 1fr;align-items:center;gap:8px;margin-bottom:16px;">

                <!-- Away team -->
                <div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:700;
                                color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:2px;">
                        {game['away_name']}
                    </div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:3.8rem;font-weight:800;
                                color:#FFFFFF;line-height:1;">{away_score}</div>
                    <div style="font-size:0.72rem;color:#4B5563;margin-top:4px;">SP: {away_sp}</div>
                </div>

                <!-- VS -->
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:600;
                            color:#374151;text-align:center;">VS</div>

                <!-- Home team -->
                <div style="text-align:right;">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1rem;font-weight:700;
                                color:#6B7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:2px;">
                        {game['home_name']}
                    </div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:3.8rem;font-weight:800;
                                color:#FFFFFF;line-height:1;">{home_score}</div>
                    <div style="font-size:0.72rem;color:#4B5563;margin-top:4px;">SP: {home_sp}</div>
                </div>
            </div>

            {wp_html}
        </div>
        """, height=310 if wp_html else 230, scrolling=False)

        with st.expander("View Full Line Score"):
            ls_data = statsapi.linescore(game['game_id'])
            st.code(ls_data, language=None)

    except:
        st.warning("No Angels game data found.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── UPCOMING SCHEDULE STRIP ──
    st.markdown('<div class="section-label">Next 7 Days</div><div class="section-title">Upcoming Schedule</div>', unsafe_allow_html=True)
    strip_games = get_schedule_strip()
    if strip_games:
        strip_cols = st.columns(min(len(strip_games), 7))
        for i, g in enumerate(strip_games[:7]):
            gtime, gdate = parse_game_time(g.get('game_datetime', ''))
            is_home = g['home_name'] == 'Los Angeles Angels'
            opponent = g['away_name'] if is_home else g['home_name']
            opp_short = opponent.split()[-1]
            ha_label  = "vs" if is_home else "@"
            with strip_cols[i]:
                components.html(f"""
                <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
                <div style="background:#0D1117;border:1px solid #1E2530;border-radius:8px;
                            padding:10px 8px;text-align:center;">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;font-weight:700;
                                letter-spacing:0.15em;text-transform:uppercase;color:#6B7280;">{gdate}</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:800;
                                color:#FFFFFF;margin:4px 0;">{ha_label} {opp_short}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#9CA3AF;">{gtime}</div>
                    <div style="margin-top:6px;display:inline-block;background:{"#0d2b0d" if is_home else "#1a0d00"};
                                color:{"#22c55e" if is_home else "#f97316"};border:1px solid {"#1a4a1a" if is_home else "#3d2200"};
                                font-family:'Barlow Condensed',sans-serif;font-size:0.58rem;font-weight:700;
                                letter-spacing:0.1em;text-transform:uppercase;padding:2px 7px;border-radius:3px;">
                        {"HOME" if is_home else "AWAY"}
                    </div>
                </div>""", height=110, scrolling=False)
    else:
        st.info("Schedule loading…")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── STATS TABLES ──
    st.markdown('<div class="section-label">Fangraphs · 2026</div><div class="section-title">Team Performance</div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Batting Leaders", "Pitching Leaders"])
    with t1:
        df_bat = get_advanced_stats("batting")
        if not df_bat.empty:
            st.dataframe(df_bat.sort_values("wRC+", ascending=False).reset_index(drop=True),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Batting stats loading…")
    with t2:
        df_pit = get_advanced_stats("pitching")
        if not df_pit.empty:
            st.dataframe(df_pit.sort_values("ERA").reset_index(drop=True),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Pitching stats loading…")

# ══════════════════════════════════════════════
# RIGHT: SIDEBAR
# ══════════════════════════════════════════════
with col_side:

    # ── PLAYER SPOTLIGHT ──
    day_idx = date.today().timetuple().tm_yday
    spot = SPOTLIGHTS[day_idx % len(SPOTLIGHTS)]
    st.markdown('<div class="section-label">Player Spotlight</div>', unsafe_allow_html=True)
    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <div style="background:linear-gradient(135deg,#0D1117,#12050a);border:1px solid #2a0a12;
                border-left:4px solid #BA0021;border-radius:10px;padding:18px 20px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
            <div style="font-size:2rem;">{spot["emoji"]}</div>
            <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;font-weight:800;
                            color:#FFFFFF;line-height:1;">{spot["name"]}</div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;font-weight:700;
                            letter-spacing:0.2em;text-transform:uppercase;color:#BA0021;">{spot["pos"]}</div>
            </div>
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#C9D1D9;line-height:1.55;margin-bottom:10px;">
            {spot["stats"]}
        </div>
        <div style="background:#0a0a0a;border:1px solid #1E2530;border-radius:6px;padding:10px 12px;">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.6rem;font-weight:700;
                        letter-spacing:0.18em;text-transform:uppercase;color:#6B7280;margin-bottom:4px;">Did you know?</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.78rem;color:#9CA3AF;line-height:1.5;">
                {spot["fun"]}
            </div>
        </div>
    </div>""", height=260, scrolling=False)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── AL WEST STANDINGS ──
    st.markdown('<div class="section-label">AL West</div><div class="section-title">Standings</div>', unsafe_allow_html=True)
    standings_df = get_standings_table()
    if not standings_df.empty:
        rows_html = ""
        for _, row in standings_df.iterrows():
            is_angels   = "Angels" in row['Team']
            name_color  = "#BA0021" if is_angels else "#E8ECF0"
            name_weight = "700" if is_angels else "500"
            gb_display  = "—" if str(row['GB']) in ("0", "0.0", "") else row['GB']
            rows_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:9px 0;border-bottom:1px solid #1E2530;font-size:0.85rem;">
                <span style="color:{name_color};font-weight:{name_weight};font-family:'Inter',sans-serif;">{row['Team']}</span>
                <span style="color:#9CA3AF;font-family:'Barlow Condensed',sans-serif;font-size:1rem;">{row['W']}–{row['L']}</span>
                <span style="color:#6B7280;font-size:0.8rem;width:30px;text-align:right;">{gb_display}</span>
            </div>"""
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-radius:10px;padding:16px 20px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;
                        font-size:0.65rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#6B7280;">
                <span>Team</span><span>W–L</span><span>GB</span>
            </div>
            {rows_html}
        </div>""", height=len(standings_df) * 44 + 80, scrolling=False)
    else:
        st.info("Standings loading…")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── WEATHER ──
    st.markdown('<div class="section-label">Angel Stadium · Anaheim</div><div class="section-title">Weather</div>', unsafe_allow_html=True)
    wx = get_anaheim_weather()
    if wx:
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-radius:10px;padding:16px 20px;">
            <div style="display:flex;align-items:flex-end;gap:12px;margin-bottom:12px;">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:3rem;font-weight:800;
                            color:#FFFFFF;line-height:1;">{wx['temp']}°F</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.85rem;color:#9CA3AF;
                            padding-bottom:6px;">{wx['desc']}</div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div style="background:#111827;border-radius:6px;padding:8px 10px;">
                    <div style="font-size:0.6rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:2px;">Feels Like</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:#E8ECF0;">{wx['feels']}°F</div>
                </div>
                <div style="background:#111827;border-radius:6px;padding:8px 10px;">
                    <div style="font-size:0.6rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:2px;">Humidity</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:#E8ECF0;">{wx['humidity']}%</div>
                </div>
                <div style="background:#111827;border-radius:6px;padding:8px 10px;">
                    <div style="font-size:0.6rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:2px;">Wind</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:#E8ECF0;">{wx['wind']} mph</div>
                </div>
                <div style="background:#111827;border-radius:6px;padding:8px 10px;">
                    <div style="font-size:0.6rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:2px;">Location</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:700;color:#E8ECF0;">Anaheim</div>
                </div>
            </div>
        </div>""", height=200, scrolling=False)
    else:
        st.info("Weather loading…")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── INJURY REPORT ──
    st.markdown('<div class="section-label">Injury Report</div><div class="section-title">IL Tracker</div>', unsafe_allow_html=True)
    injuries = get_injury_report()
    if injuries:
        rows_html = ""
        for line in injuries:
            parts = line.split()
            # Typical format: #NUM POS First Last - Status
            name_str = ' '.join(parts[2:]) if len(parts) > 2 else line
            rows_html += f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #1E2530;">
                <div style="width:8px;height:8px;border-radius:50%;background:#BA0021;flex-shrink:0;"></div>
                <div style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#E8ECF0;">{name_str}</div>
            </div>"""
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-left:3px solid #BA0021;
                    border-radius:10px;padding:14px 18px;">
            {rows_html}
        </div>""", height=len(injuries) * 38 + 30, scrolling=False)
    else:
        st.info("No injury data available.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── HALOS HEADLINES ──
    st.markdown('<div class="section-label">Angels Coverage</div><div class="section-title">Halos Headlines</div>', unsafe_allow_html=True)
    angels_news = get_rss_news('https://www.mlb.com/angels/feeds/news/rss.xml', 'mlb', limit=8)
    if angels_news:
        items_html = ""
        for item in angels_news:
            items_html += f"""
            <div style="border-bottom:1px solid #1E2530;padding:11px 0;">
                <a href="{item['url']}" target="_blank"
                   style="font-family:'Inter',sans-serif;font-size:0.84rem;font-weight:500;
                          color:#E8ECF0;line-height:1.45;text-decoration:none;display:block;margin-bottom:5px;">
                    {item['title']}
                </a>
                <div style="font-size:0.7rem;color:#6B7280;">{item['meta']}</div>
            </div>"""
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-radius:10px;padding:12px 18px;">
            {items_html}
        </div>""", height=len(angels_news) * 72 + 20, scrolling=False)
    else:
        st.info("Angels headlines loading…")

# ─────────────────────────────────────────────
# DID YOU KNOW — Fun Facts
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Did You Know?</div><div class="section-title" style="margin-bottom:4px;">⚡ Halos & Baseball Facts</div>', unsafe_allow_html=True)

FUN_FACTS = [
    ("🎯", "Zach Neto's Cannon Arm", "#0085CA",
     "Zach Neto posted one of the highest arm-strength grades among all MLB shortstops in 2024, regularly hitting throws of 95+ mph. He's built like a quarterback playing shortstop."),
    ("🔥", "The Rally Monkey Origin", "#BA0021",
     "The Rally Monkey was born on June 6, 2000 when a stadium video operator played a clip from the movie 'Ace Ventura' during a late-inning comeback. It became one of baseball's most iconic traditions."),
    ("⚡", "Mike Trout's All-Time WAR Pace", "#FFD700",
     "Mike Trout accumulated more career WAR by age 26 than any player in MLB history — including Willie Mays and Mickey Mantle. He did it in a small market with zero playoff wins."),
    ("🌊", "The Big A Halo Tradition", "#22c55e",
     "The giant halo atop Angel Stadium lights up red after every Angels home win. It's been doing it since 1966 and is one of the most recognized landmarks in all of Anaheim."),
    ("🎲", "Baseball's Weird Math", "#9CA3AF",
     "A .300 batting average is considered excellent — but it means the hitter fails 70% of the time. No other major sport celebrates failure at that rate as a sign of greatness."),
    ("💥", "Exit Velocity is Everything", "#FF6600",
     "A ball hit at 95 mph has roughly a 30% chance of being a hit. At 100+ mph? Over 50%. At 110 mph it's nearly automatic. The Angels track this obsessively in player development."),
    ("🏟️", "Angel Stadium's Age", "#0085CA",
     "Angel Stadium opened in 1966, making it the third-oldest ballpark in the American League. Only Fenway Park (1912) and Wrigley Field (1914) are older among active MLB parks."),
    ("🧢", "Nolan Ryan's Angels Years", "#BA0021",
     "Nolan Ryan pitched for the Angels from 1972–1979 and threw 4 of his 7 no-hitters in Anaheim. He struck out a then-record 383 batters in a single season (1973) as an Angel."),
    ("📐", "The Shift is Gone", "#22c55e",
     "MLB banned the defensive shift before the 2023 season. Batting averages league-wide jumped nearly 10 points the first year — exactly as predicted."),
    ("🎯", "Pitch Framing is Worth Wins", "#FFD700",
     "Pitch framing — how a catcher presents a pitch to steal borderline strikes — is worth up to 2–3 wins per year for an elite backstop."),
    ("🚀", "High Spin = Rising Fastball", "#FF6600",
     "A four-seam fastball with high spin rate (2,400+ RPM) appears to 'rise' because it drops less than the hitter's brain expects. It's an optical illusion baked into physics."),
    ("💡", "Why Stolen Bases Came Back", "#0085CA",
     "After years of decline, stolen bases surged in 2023 after MLB increased base sizes by 3 inches and limited pickoff attempts. Speed became a weapon again overnight."),
    ("🏆", "2002: The Greatest Comeback", "#BA0021",
     "The Angels trailed the Giants 3-2 in games and were down 3 runs with 8 outs left in Game 6. They tied it, won in extras, then won Game 7 the next night. Still the only title in franchise history."),
    ("🧠", "WAR Explained Simply", "#9CA3AF",
     "WAR asks: how many wins did this player add vs a replacement-level minor leaguer? 2 WAR = solid starter. 5+ = All-Star. 8+ = MVP candidate. Trout once posted a 10.5."),
    ("🎵", "Gene Autry's Wild Bet", "#22c55e",
     "Gene Autry only wanted an LA radio broadcast license. MLB said he had to buy a team to get it. He paid $2.1M for the Angels in 1961. The franchise is now worth over $2 billion."),
]

fact_cols = st.columns(3)
for col_i, col in enumerate(fact_cols):
    fact = FUN_FACTS[(day_idx + col_i) % len(FUN_FACTS)]
    icon, label, color, text = fact
    with col:
        components.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
        <div style="background:#0D1117;border:1px solid #1E2530;border-top:3px solid {color};
                    border-radius:10px;padding:18px 20px;height:100%;box-sizing:border-box;">
            <div style="font-size:1.8rem;margin-bottom:8px;">{icon}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;font-weight:700;
                        letter-spacing:0.2em;text-transform:uppercase;color:{color};margin-bottom:6px;">{label}</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.84rem;color:#C9D1D9;line-height:1.6;">{text}</div>
        </div>""", height=210, scrolling=False)

# ─────────────────────────────────────────────
# MLB NEWS
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Around the Majors</div><div class="section-title" style="margin-bottom:4px;">📰 MLB News</div>', unsafe_allow_html=True)

mlb_news, BADGE_STYLES = get_mlb_general_news()
if mlb_news:
    left_col, right_col = st.columns(2)
    for i, item in enumerate(mlb_news[:16]):
        col = left_col if i % 2 == 0 else right_col
        color, bg, border = BADGE_STYLES[item['key']]
        badge = (f'<span style="font-family:\'Barlow Condensed\',sans-serif;font-size:0.6rem;font-weight:700;'
                 f'letter-spacing:0.12em;text-transform:uppercase;padding:2px 7px;border-radius:3px;'
                 f'background:{bg};color:{color};border:1px solid {border};display:inline-block;">{item["source"]}</span>')
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
        </div>"""
        with col:
            components.html(card_html, height=115, scrolling=False)
else:
    st.info("MLB news loading…")

# ─────────────────────────────────────────────
# CHEAT SHEET
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("🎓  Water Cooler Cheat Sheet — Sound Smart Today"):
    left, right = st.columns(2)
    with left:
        st.markdown("""
        <div class="section-label">Hitting</div>
        <p><span class="stat-term">wRC+</span><br>
        <span class="stat-def">Weighted Runs Created Plus. 100 is league average; 150 is elite.</span></p>
        <p><span class="stat-term">HardHit%</span><br>
        <span class="stat-def">Balls hit over 95 mph. High % = consistent quality contact.</span></p>
        <p><span class="stat-term">OPS</span><br>
        <span class="stat-def">On-base + Slugging. Over .850 is very good. Simple but noisy.</span></p>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("""
        <div class="section-label">Pitching</div>
        <p><span class="stat-term">FIP</span><br>
        <span class="stat-def">ERA without the luck — only counts Ks, BBs, HRs. True skill indicator.</span></p>
        <p><span class="stat-term">WHIP</span><br>
        <span class="stat-def">Walks + Hits per inning. Under 1.10 is ace territory.</span></p>
        <p><span class="stat-term">K/9</span><br>
        <span class="stat-def">Strikeouts per 9 innings. 10+ is electric stuff.</span></p>
        """, unsafe_allow_html=True)
