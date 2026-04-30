/* 進入挑戰按鈕：強制讓外層容器變為 Flex 並置中 */
    [data-testid="stFormSubmitButton"] {
        display: flex !important;
        justify-content: center !important; /* 水平置中 */
        width: 100% !important;
        margin-top: 25px !important;
    }

    /* 針對按鈕本身調整寬度 */
    [data-testid="stFormSubmitButton"] button {
        width: auto !important;         /* 關鍵：寬度設為自動，不再拉長 */
        min-width: 150px !important;    /* 設定一個最小寬度，看起來比較大方 */
        background-color: {COLOR_MAIN} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 40px !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }
