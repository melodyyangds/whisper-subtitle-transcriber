# Whisper Subtitle Transcriber：Windows 語音轉文字與字幕工具

[English README](README.md) · [完整英文使用指南](docs/USAGE.md) · [疑難排解](TROUBLESHOOTING.md) · [測試紀錄](VALIDATION.md)

這個專案包含英文版和中英混合版，可將電腦中的音訊或影片轉成 TXT 逐字稿與 SRT 字幕。辨識在本機 CPU 執行，不需要 NVIDIA 顯示卡、API 金鑰或付費轉錄服務。

## 選擇版本

| 版本 | 適用內容 | 資料夾 | 啟動方式 |
| --- | --- | --- | --- |
| 英文版 | 英文錄音或影片 | `English_Video_Transcriber_Windows` | 將檔案拖到 `Transcribe_Video.bat` |
| 中英混合版 | 中文為主、穿插英文的內容 | `Bilingual_Subtitles_Windows_v3` | 雙擊 `Transcribe_Audio_Video.bat` 選檔，或將檔案拖上去 |

中英混合版會保留辨識出的英文，並將中文轉成台灣繁體中文。輸出是一份逐字稿與一條字幕軌，沒有另外產生中英文對照翻譯。

## 第一次使用

1. 安裝 **64 位元 Python 3.10～3.12**；本專案以 Python 3.12 測試。安裝時勾選 **Add python.exe to PATH**。
2. 在 [GitHub 專案頁](https://github.com/melodyyangds/whisper-subtitle-transcriber) 選擇 **Code → Download ZIP**。
3. 完整解壓縮，保留各版本資料夾內的 Python、PowerShell、BAT 與 requirements 檔案。
4. 開啟所需版本的資料夾，依上表啟動。建議先用短錄音確認流程。
5. 第一次執行會安裝套件並下載模型，請保持網路連線與視窗開啟。
6. 完成後，在原始錄音或影片旁找到輸出檔案。

啟動器會建立各自的 `.venv` 環境。若找不到合適的 Python，會嘗試透過 `winget` 安裝 Python 3.12；遇到安裝限制時，可以先自行安裝 Python。

英文 BAT 需要拖入檔案，直接雙擊會顯示操作提示。中英混合版可雙擊選檔，另有 `Transcribe_Higher_Accuracy.bat` 使用較大的 `medium` 模型，CPU 執行時間與記憶體需求也較高。

## 輸出與注意事項

例如輸入 `meeting.mp4`，會在同一資料夾產生：

```text
meeting_transcript.txt
meeting_subtitles.srt
```

- TXT 可用記事本開啟；SRT 可作為外掛字幕載入相容的影片播放器。
- 原始錄音或影片不會被修改；再次執行相同輸入會覆寫同名的 TXT 與 SRT，請先備份要保留的結果。
- 人名、專有名詞、數字、安靜片段與語言切換可能辨識錯誤，對外使用前請校對。
- 程式逐段寫入，執行中斷時可能留下尚未完成的輸出檔。

常見輸入包括 MP4、M4A、MP3、WAV、MOV、MKV、FLAC 等，實際支援仍取決於檔案內的編碼與是否包含有效音軌。每次處理一個檔案。

## 隱私與離線使用

程式在本機處理錄音，沒有將內容送到付費語音 API。首次安裝套件及下載模型需要網路；必要的套件與模型已快取後，可離線辨識。切換尚未下載的模型仍需要首次下載。

此儲存庫不包含私人錄音、產生的逐字稿、字幕、虛擬環境、模型檔或憑證。

## 測試狀態

英文版已使用 11 秒的公開英文語音樣本，分別通過 Python、Windows PowerShell 與 BAT 的實際 CPU 轉錄，並檢查 TXT、SRT、時間戳與預期語句。另有 13 項自動化回歸測試。

中英混合版先前已由專案擁有者在 Windows 成功使用，公開整理時保留原有八個檔案，並通過套件與回歸檢查；沒有另外宣稱完成新的中英混合語音準確度測試。

詳細安裝、手動執行、模型及語言參數請參閱 [完整使用指南](docs/USAGE.md)。遇到問題可查閱 [疑難排解](TROUBLESHOOTING.md)，或在 GitHub 提出 issue；分享錯誤訊息前請移除私人路徑及逐字稿內容。
