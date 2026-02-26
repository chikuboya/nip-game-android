[app]
# アプリの名前
title = Nip Strategy Game

# パッケージ名（英小文字。ドメイン形式）
package.name = nipgame
package.domain = org.test

# ソースコードのある場所（カレントディレクトリ）
source.dir = .

# 含めるファイルの拡張子（★ここに ttc を追加済み）
source.include_exts = py,png,jpg,kv,atlas,ttc

# バージョン
version = 0.1

# 必要な権限（特になし）
android.permissions = INTERNET

# 画面の向き（縦向き固定に設定）
orientation = portrait

# --- 以下はビルド用の設定（基本そのままでOK） ---
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
python_for_android_branch = master
