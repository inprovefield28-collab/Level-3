import streamlit as st
import pandas as pd
import os
import re
import random

# ==========================================
# 老師修改區
# ==========================================
APP_TITLE = "文法句型快樂學習"
INTRO_BOX_TEXT = """
**本次優化重點：**

• 介係詞統一：surprised 搭配使用 **at**
• 邏輯除錯：修正人/物主詞與 V-ed/V-ing 的配對
• 100 題去重：每題皆為獨立情境與描述
• 格式標準：句首大寫、專有名詞保護
"""

COLOR_MAIN = "#8B5CF6"   # 主色
COLOR_LIGHT = "#F5F3FF"  # 說明框背景
COLOR_BG = "#F8F9FD"     # 網頁底色
# ==========================================

st.set_page_config(page_title=APP_TITLE, layout="centered")

# --- 1. 樣式注入 (核心：將 st.form 偽裝成您的白色卡片) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_BG}; }}
    header {{ visibility: hidden; }}
    
    /* 針對 st.form 進行樣式重寫 */
    [data-testid="stForm"] {{
        background-color: white !important;
        padding: 40px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        border: none !important;
        border-top: 10px solid {COLOR_MAIN} !important;
        max-width: 600px;
        margin: 20px auto;
    }}
    
    .app-title {{
        color: {COLOR_MAIN};
        font-weight: 800;
        font-size: 36px;
        margin-bottom: 30px;
        text-align: center;
    }}
    
    .intro-box {{
        background-color: {COLOR_LIGHT};
        padding: 25px;
        border-radius: 12px;
        color: {COLOR_MAIN};
        font-size: 15px;
        line-height: 1.8;
        margin-bottom: 30px;
        white-space: pre-wrap;
        text-align: left;
    }}

    /* 輸入框外觀 */
    .stTextInput input {{
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 10px !important;
    }}

    /* 按鈕樣式 (進入挑戰) */
    [data-testid="stFormSubmitButton"] button {{
        width: 100% !important;
        background-color: {COLOR_MAIN} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 22px !important;
        font-weight: bold !important;
    }}

    /* 測驗選項按鈕 (非 form 內元件) */
    .quiz-btn button {{
        width: 100% !important;
        background-color: white !important;
        color: #333 !important;
        border: 2px solid #F3F4F6 !important;
        text-align: left !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心功能 ---
@st.cache_data
def load_and_shuffle_data():
    df_list = []
    file_pattern = re.compile(r"([a-zA-Z0-9]+)(\d+-\d+)\.csv$")
    all_files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for file_name in all_files:
        match = file_pattern.match(file_name)
        if match:
            cat, rng = match.group(1), match.group(2)
            try:
                temp_df = pd.read_csv(file_name, encoding='utf-8-sig')
            except:
                temp_df = pd.read_csv(file_name, encoding='big5')
            temp_df.columns = [c.strip().lower() for c in temp_df.columns]
            temp_df['cat'], temp_df['rng'] = cat, rng
            df_list.append(temp_df)
    
    if not df_list: return []
    full_df = pd.concat(df_list, ignore_index=True)
    questions = []
    for q in full_df.to_dict('records'):
        opts = [str(q.get('a','')), str(q.get('b','')), str(q.get('c',''))]
        correct_text = opts[0]
        random.shuffle(opts)
        questions.append({
            'id': str(q.get('id', 0)).zfill(3),
            'q': q.get('question', ''),
            'opts': opts,
            'ans': opts.index(correct_text),
            'path': f"audio_{q['cat']}{q['rng']}/q_{str(q.get('id', 0)).zfill(3)}.mp3",
            'level_info': f"{q['cat']}{q['rng']}"
        })
    return questions

if 'step' not in st.session_state:
    st.session_state.step = 'start'

# A. 首頁
if st.session_state.step == 'start':
    # 使用 st.form 確保所有元件被包在同一個 div 結構中
    with st.form("start_form"):
        st.markdown(f'<div class="app-title">{APP_TITLE}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="intro-box">{INTRO_BOX_TEXT}</div>', unsafe_allow_html=True)
        
        user_name = st.text_input("user_name", label_visibility="collapsed", placeholder="請輸入姓名")
        
        submit = st.form_submit_button("進入挑戰")
        
        if submit:
            if user_name.strip() == "":
                st.error("請輸入姓名後再開始唷！")
            else:
                st.session_state.user_name = user_name
                st.session_state.all_pool = load_and_shuffle_data()
                if not st.session_state.all_pool:
                    st.error("找不到題庫檔案 (CSV)")
                else:
                    st.session_state.quiz_data = random.sample(st.session_state.all_pool, min(len(st.session_state.all_pool), 10))
                    st.session_state.current_idx = 0
                    st.session_state.results = []
                    st.session_state.step = 'quiz'
                    st.rerun()

# B. 測驗頁
elif st.session_state.step == 'quiz':
    q = st.session_state.quiz_data[st.session_state.current_idx]
    st.markdown(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    if os.path.exists(q['path']):
        st.audio(q['path'])
    st.write(f"#### {q['q']}")
    
    st.markdown('<div class="quiz-btn">', unsafe_allow_html=True)
    keys = ['A', 'B', 'C']
    for i, opt_text in enumerate(q['opts']):
        if st.button(f"{keys[i]}. {opt_text}", key=f"q_{st.session_state.current_idx}_{i}"):
            st.session_state.results.append({
                "question": q['q'],
                "user_choice": opt_text,
                "correct_answer": q['opts'][q['ans']],
                "is_correct": (i == q['ans'])
            })
            st.session_state.current_idx += 1
            if st.session_state.current_idx >= 10:
                st.session_state.step = 'result'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# C. 結果頁
elif st.session_state.step == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>🏆 練習結束！</h2>", unsafe_allow_html=True)
    score = sum(1 for item in st.session_state.results if item['is_correct'])
    final_score = score * 10
    st.markdown(f"<h3 style='text-align:center; color:{COLOR_MAIN};'>得分：{final_score} 分</h3>", unsafe_allow_html=True)

    wrong_txt = ""
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_txt += f"Q{i+1}: {item['question']}\\n   ❌ 您選: {item['user_choice']}\\n   ✅ 正確: {item['correct_answer']}\\n\\n"
    
    level_tag = st.session_state.quiz_data[0]['level_info']
    report_text = f"【{APP_TITLE}】\\n姓名：{st.session_state.user_name}\\n成績：{final_score}\\n\\n{wrong_txt}"

    html_code = f"""
        <button id="copyBtn" style="background-color:{COLOR_MAIN}; color:white; border:none; padding:15px; font-size:20px; font-weight:bold; border-radius:15px; width:100%; cursor:pointer;">
            按我複製成績給老師
        </button>
        <script>
            document.getElementById('copyBtn').onclick = function() {{
                const text = "{report_text}";
                navigator.clipboard.writeText(text.replace(/\\\\n/g, '\\n')).then(function() {{
                    document.getElementById('copyBtn').innerText = '✅ 複製成功！';
                    setTimeout(function() {{ document.getElementById('copyBtn').innerText = '按我複製成績給老師'; }}, 2000);
                }});
            }};
        </script>
    """
    st.components.v1.html(html_code, height=100)

    st.write("---")
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            st.error(f"**Q{i+1}: {item['question']}**\n\n❌ 您選: {item['user_choice']}  \n✅ 正確: {item['correct_answer']}")

    if st.button("再玩一次"):
        st.session_state.step = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
