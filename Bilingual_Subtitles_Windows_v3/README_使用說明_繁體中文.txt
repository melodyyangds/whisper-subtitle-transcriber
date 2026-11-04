Windows 中英混合字幕工具 v3：修正 Windows PowerShell 套件驗證錯誤
=============================================================

【如果你上一版已顯示 Successfully installed ...】
你不需要刪除 .venv，也不需要重裝套件！
請把新版的 transcribe.ps1 和 verify_install.py 複製到你目前正在使用的
Bilingual_Subtitles_Complete_Windows_FIXED 資料夾，覆蓋 transcribe.ps1。
(也可下載單獨的 HOTFIX 修補包，裡面只有這兩個檔案。)
接著重跑 Transcribe_Higher_Accuracy.bat。

【若是第一次安裝，沒有舊版 .venv】
直接解壓縮完整 v3 ZIP 到新資料夾，並執行 BAT；第一次仍需安裝套件。

【支援格式】
.m4a, .mp3, .wav, .mp4, .mov, .mkv, .flac, .ogg, .webm, .aac, .wma

【啟動方式】
雙擊 Transcribe_Audio_Video.bat 選擇檔案 (small 模型，較快)
或雙擊 Transcribe_Higher_Accuracy.bat 選擇檔案 (medium 模型，較慢)
也可將音檔直接拖到任一 BAT。

【輸出】
原音檔旁產生 _transcript.txt 和 _subtitles.srt。
中英混合原文保留，中文轉台灣繁體；少數英文專有名詞可能需校對。

【本次修正原因】
上一版把一段含雙引號的 Python 程式碼透過 PowerShell 傳給 python -c。
Windows PowerShell 的原生命令引數處理剝掉了 Python 程式碼中的引號，
造成 split(.) / print(OK) SyntaxError。v3 改為直接執行 verify_install.py，
不經過 -c 字串，因此不再依賴有問題的引號跳脫。

【驗證範圍】
已做 Python 語法、修補位置、套件 mock 驗證與 ZIP 內容測試。
目前沒有原生 Windows PowerShell 執行環境，也沒有你的實際錄音。
