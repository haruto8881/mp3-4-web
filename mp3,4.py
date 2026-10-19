import os
import streamlit as st
import yt_dlp
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

st.set_page_config(
    page_title="YouTube Media Downloader",
    page_icon="🎬",
    layout="centered"
)

# 画面の左側にスマホ用の接続アドレスを表示します
with st.sidebar:
    st.header("📱 スマホからのアクセス方法")
    local_ip = get_local_ip()
    st.write("パソコンと同じWi-Fiに接続したスマホのブラウザで、以下のURLにアクセスしてください：")
    st.code(f"http://{local_ip}:8501", language="text")
    st.caption("※パソコンで「streamlit run」を起動したままにしてください。")

st.title("🎬 YouTube MP3 / MP4 Downloader")
st.write("YouTubeのURLを入力して、音楽（MP3）または動画（MP4）としてダウンロードする個人用ツールです。")

url = st.text_input(
    "YouTubeのURLを入力してください:",
    placeholder="https://www.youtube.com/watch?v=..."
)

download_format = st.radio(
    "ダウンロード形式を選択してください:",
    ("MP3 (音声のみ)", "MP4 (動画付き)")
)

if st.button("ダウンロードを実行"):
    if not url:
        st.warning("YouTubeのURLを入力してください。")
    else:
        format_name = "MP4動画" if "MP4" in download_format else "MP3音声"
        with st.spinner(f"動画を読み込んで{format_name}に変換しています... 少々お待ちください。"):
            output_template = "downloaded_media.%(ext)s"
            
            # 形式に応じたオプション設定（クッキーと403エラー対策を追加）
            if "MP4" in download_format:
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': output_template,
                    'noplaylist': True,
                    'merge_output_format': 'mp4',
                    'nocheckcertificate': True,
                    'cookiefile': 'cookie.txt',  # クッキーファイルを読み込む設定
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                        }
                    }
                }
                target_ext = "mp4"
                mime_type = "video/mp4"
                button_label = "📥 MP4動画ファイルをダウンロード"
            else:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'cookiefile': 'cookie.txt',  # クッキーファイルを読み込む設定
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    },
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                        }
                    },
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                target_ext = "mp3"
                mime_type = "audio/mp3"
                button_label = "📥 MP3音楽ファイルをダウンロード"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get('title', 'media')
                    
                    safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
                    if not safe_title:
                        safe_title = "downloaded_media"
                        
                    final_filename = f"{safe_title}.{target_ext}"
                    temp_filename = f"downloaded_media.{target_ext}"
                    
                    if os.path.exists(temp_filename):
                        if os.path.exists(final_filename):
                            os.remove(final_filename)
                        os.rename(temp_filename, final_filename)
                    else:
                        for file in os.listdir("."):
                            if file.startswith("downloaded_media.") and file.endswith(target_ext):
                                if os.path.exists(final_filename):
                                    os.remove(final_filename)
                                os.rename(file, final_filename)
                                break
                        else:
                            final_filename = temp_filename

                st.success(f"「{title}」の変換が完了しました！")

                with open(final_filename, "rb") as f:
                    st.download_button(
                        label=button_label,
                        data=f,
                        file_name=final_filename,
                        mime=mime_type
                    )

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
