[app]
title = Nip Strategy Game
package.name = nipgame
package.domain = org.test
source.dir = .
# 日本語フォントを含める設定
source.include_exts = py,png,jpg,kv,atlas,ttc,ttf
version = 0.1
requirements = python3,kivy==2.3.1,kivy_deps.sdl2,kivy_deps.glew,kivy_deps.angle

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
