import streamlit as st
import pandas as pd
import os
import re
import random

# --- 1. 初始化與設定模式 ---
# 使用 sidebar 作為老師的控制台
st.sidebar.header("⚙️ 老師控制台")
config_mode = st.sidebar.checkbox("開啟編輯模式 (調整樣式與文字)")

# 可動參數設定
app_title = st.sidebar.text_input("大標題", "文法句型快樂學習")
app_subtitle = st.sidebar.text_input("副標題", "U12 情緒動詞 (2026 文法精校版)")
intro_text = st.sidebar.text_area("說明小框文字 (可多行)", "本次優化重點：\n• 介係詞統一：surprised 搭配使用 at\n• 邏輯除錯：修正人/物主詞與 V-ed/V-ing 的配對\n• 100 題去重：每題皆為獨立情境與描述")
font_size = st.sidebar.slider("文字大小 (px)", 18, 32, 22)

# 主題色設定 (一深一淺搭配)
themes = {
    "活力紫": {"main": "#8B5CF6", "light": "#EDE9FE"},
    "森林綠": {"main": "#10B981", "light": "#D1FAE5"},
    "天空藍": {"main": "#3B82F6", "light": "#DBEAFE"},
    "夕陽橙": {"main": "#F59E0B", "light": "#FEF3C7"},
    "冷酷灰": {"main": "#4B5563", "light": "#F3F4F6"}
}
theme_choice = st.sidebar.selectbox("切換主題色", list(themes.keys()))
color_main = themes[theme_choice]["main"]
color_light = themes[theme_choice]["light"]

# --- 2. 樣式注入 ---
st.markdown(f"""
    <style>
    /* 全域按鈕樣式 */
    div.stButton > button {{
        width: 100% !important;
        background-color: white !important;
        border: 2px solid {color_light} !important;
        border-radius: 15px !important;
        padding: 15px !important;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        border-color: {color_main} !important;
        background-color: {color_light} !important;
    }}
    div.stButton > button p {{
        font-size: {font_size}px !important;
        font-weight: bold !important;
        color: #333;
    }}
    /* 進入挑戰大按鈕 */
    .main-btn button {{
        background-color: {color_main} !important;
        color: white !important;
    }}
    .main-btn button p {{
        color: white !important;
    }}
    /* 說明框樣式 */
    .intro-box {{
        background-color: {color_light};
        padding: 20px;
        border-radius: 15px;
        color: {color_main};
        font-size: 16px;
        margin-bottom: 25px;
        white-space: pre-wrap;
        border-left: 5px solid {color_main};
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料讀取邏輯 (全 A 隨機化) ---
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
        correct_text = opts[0] # 你的需求：原始檔 A 永遠是對的
        random.shuffle(opts)
        questions.append({
            'id': str(q.get('id', 0)).zfill(3),
            'q': q.get('question', ''),
            'opts': opts,
            'ans': opts.index(correct_text),
            'path': f"audio_{q['cat']}{q['rng']}/q_{str(q.get('id', 0)).zfill(3)}.mp3"
        })
    return questions

# --- 4. 流程控制 ---
if 'step' not in st.session_state:
    st.session_state.step = 'start'
    st.session_state.user_name = ""

# A. 開始頁面
if st.session_state.step == 'start':
    st.markdown(f"<h1 style='text-align:center; color:{color_main};'>{app_title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:gray;'>{app_subtitle}</p>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='intro-box'>{intro_text}</div>", unsafe_allow_html=True)
    
    st.session_state.user_name = st.text_input("請輸入姓名：", placeholder="例如：Student A")
    
    st.write("##")
    if st.button("進入挑戰", key="start_btn"):
        if st.session_state.user_name.strip() == "":
            st.warning("請先輸入姓名喔！")
        else:
            st.session_state.all_pool = load_and_shuffle_data()
            st.session_state.quiz_data = random.sample(st.session_state.all_pool, min(len(st.session_state.all_pool), 10))
            st.session_state.current_idx = 0
            st.session_state.results = []
            st.session_state.step = 'quiz'
            st.rerun()

# B. 測驗頁面
elif st.session_state.step == 'quiz':
    q = st.session_state.quiz_data[st.session_state.current_idx]
    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    
    if os.path.exists(q['path']):
        st.audio(q['path'])
    
    st.write(f"#### {q['q']}")
    
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

# C. 結果頁面
elif st.session_state.step == 'result':
    st.markdown(f"<h2 style='text-align:center;'>🏆 練習結束，{st.session_state.user_name}！</h2>", unsafe_allow_html=True)
    score = sum(1 for item in st.session_state.results if item['is_correct'])
    final_score = score * 10
    st.markdown(f"<h3 style='text-align:center; color:{color_main};'>得分：{final_score}</h3>", unsafe_allow_html=True)

    # 製作複製文字 (格式化：僅顯示錯題)
    wrong_txt = ""
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_txt += f"Q{i+1}: {item['question']}\\n   ❌ 您選: {item['user_choice']}\\n   ✅ 正確: {item['correct_answer']}\\n\\n"
    
    report_text = f"【{app_subtitle}】\\n姓名：{st.session_state.user_name}\\n成績：{final_score}\\n\\n{wrong_txt}"

    html_code = f"""
        <button id="copyBtn" style="background-color:{color_main}; color:white; border:none; padding:15px; font-size:20px; font-weight:bold; border-radius:15px; width:100%; cursor:pointer;">
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
    # 底部詳情僅顯示錯題供檢視
    st.write("🔍 錯題檢視：")
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            st.error(f"**Q{i+1}: {item['question']}**\n\n❌回答: {item['user_choice']}  |  ✅正確: {item['correct_answer']}")

    if st.button("再玩一次"):
        st.session_state.step = 'start'
        st.rerun()
