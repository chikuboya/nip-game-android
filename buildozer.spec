[app]
title = Nip Strategy Game
package.name = nipgame
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttc,ttf
version = 0.1

# 必須ライブラリを最小限に絞ります
requirements = python3,kivy

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# 重要：自動的にライセンスに同意する設定
android.accept_sdk_license = True
android.skip_update = False
