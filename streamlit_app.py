import streamlit as st
import pandas as pd
import os
import re
import random

# ==========================================
# 老師修改區：在此直接修改文字與設定
# ==========================================
APP_TITLE = "文法句型快樂學習"
APP_SUBTITLE = "U12 情緒動詞 (2026 文法精校版)"
INTRO_BOX_TEXT = """
**本次優化重點：**
• 介係詞統一：surprised 搭配使用 **at**
• 邏輯除錯：修正人/物主詞與 V-ed/V-ing 的配對
• 100 題去重：每題皆為獨立情境與描述
• 格式標準：句首大寫、專有名詞保護
"""

# 主題顏色 (比照圖片紫色系)
COLOR_MAIN = "#8B5CF6"   # 主色
COLOR_LIGHT = "#F5F3FF"  # 說明框淡紫色背景
COLOR_BG = "#F8F9FD"     # 網頁底色
# ==========================================

# --- 1. 樣式注入 (完全還原圖片視覺) ---
st.set_page_config(page_title=APP_TITLE, layout="centered")

st.markdown(f"""
    <style>
    /* 全域背景 */
    .stApp {{
        background-color: {COLOR_BG};
    }}
    
    /* 隱藏上方頂欄與選單 */
    header {{visibility: hidden;}}
    
    /* 卡片式容器 */
    .main-card {{
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-top: 8px solid {COLOR_MAIN};
        margin-top: 20px;
    }}
    
    /* 標題樣式 */
    .app-title {{
        color: {COLOR_MAIN};
        text-align: center;
        font-weight: 800;
        font-size: 32px;
        margin-bottom: 5px;
    }}
    .app-subtitle {{
        color: #6B7280;
        text-align: center;
        font-size: 16px;
        margin-bottom: 30px;
    }}
    
    /* 說明小框 */
    .intro-box {{
        background-color: {COLOR_LIGHT};
        padding: 20px;
        border-radius: 12px;
        color: {COLOR_MAIN};
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 30px;
    }}
    
    /* 輸入框標籤 */
    .input-label {{
        font-weight: bold;
        font-size: 18px;
        color: #374151;
        margin-bottom: 10px;
    }}
    
    /* 按鈕樣式 (進入挑戰) */
    div.stButton > button {{
        width: 100% !important;
        background-color: {COLOR_MAIN} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 18px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(139, 92, 246, 0.4) !important;
    }}

    /* 選項按鈕樣式 (測驗中) */
    .quiz-btn button {{
        background-color: white !important;
        color: #333 !important;
        border: 2px solid #F3F4F6 !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }}
    .quiz-btn button:hover {{
        border-color: {COLOR_MAIN} !important;
        background-color: {COLOR_LIGHT} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料讀取 (維持全 A 原始檔邏輯) ---
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
        correct_text = opts[0] # 原始檔 A 是正確答案
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

# --- 3. 測驗流程 ---
if 'step' not in st.session_state:
    st.session_state.step = 'start'

# A. 首頁 (還原 image_2885a8.png)
if st.session_state.step == 'start':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="app-title">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-subtitle">{APP_SUBTITLE}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="intro-box">{INTRO_BOX_TEXT}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="input-label">請輸入姓名：</div>', unsafe_allow_html=True)
    user_name = st.text_input("user_name_input", label_visibility="collapsed", placeholder="請輸入姓名")
    
    st.write("##") # 留空隙
    if st.button("進入挑戰"):
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
    st.markdown('</div>', unsafe_allow_html=True)

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

# C. 結果頁 (依照要求顯示錯題與複製姓名)
elif st.session_state.step == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>🏆 練習結束！</h2>", unsafe_allow_html=True)
    score = sum(1 for item in st.session_state.results if item['is_correct'])
    final_score = score * 10
    st.markdown(f"<h3 style='text-align:center; color:{COLOR_MAIN};'>得分：{final_score} 分</h3>", unsafe_allow_html=True)

    # 製作複製文字 (僅顯示錯題)
    wrong_txt = ""
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_txt += f"Q{i+1}: {item['question']}\\n   ❌ 您選: {item['user_choice']}\\n   ✅ 正確: {item['correct_answer']}\\n\\n"
    
    # 這裡的 Level 會抓取第一題的分類資訊
    level_tag = st.session_state.quiz_data[0]['level_info']
    report_text = f"【{level_tag}】\\n姓名：{st.session_state.user_name}\\n成績：{final_score}\\n\\n{wrong_txt}"

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
    st.write("🔍 錯題檢視：")
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            st.error(f"**Q{i+1}: {item['question']}**\n\n❌ 您選: {item['user_choice']}  \n✅ 正確: {item['correct_answer']}")

    if st.button("再玩一次"):
        st.session_state.step = 'start'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
