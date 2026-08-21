# EvernightPlaysMusic

一个用于播放音乐的vibe coding程序喵~꒰ঌ(˶ˆᗜˆ˵)໒꒱

由于作者习惯于把音乐下载到本地听，市面上很多音乐播放器的很多功能根本用不到，所以让AI给我写了一个喵~

## 功能特性

- **桌面宠物** — 透明背景的长夜月 GIF 动图，可拖动，右键弹出菜单
- **系统托盘** — 任务栏图标常驻，快速控制播放
- **音乐播放** — 支持 mp3、wav、ogg、flac、aac、wma、m4a 格式（主要是mp3喵~）
- **播放控制** — 播放/暂停、上一首/下一首、音量调节
- **播放模式** — 顺序播放、列表循环、单曲循环、随机播放
- **歌曲管理** — 扫描文件夹、添加单曲、全选批量操作、移除歌曲
- **收藏功能** — 添加/取消喜欢，收藏列表独立展示
- **自动恢复** — 重启后自动恢复播放列表、播放位置和所有设置
- **深色主题** — 紫色半透明 UI，带背景图片（背景是找的二创图喵~）

## 使用方式

### 下载 exe

前往 [Releases](https://github.com/renge1145141919810/EvernightPlaysMusic/releases) 下载 `EvernightPlaysMusic.exe`，双击即可运行，无需安装 Python。

### 从源码运行

```bash
git clone https://github.com/renge1145141919810/EvernightPlaysMusic.git
cd EvernightPlaysMusic
pip install PyQt5 pygame-ce mutagen
python main.py
```

## 操作说明

| 操作 | 说明 |
|------|------|
| 左键拖动小人 | 移动位置 |
| 左键双击小人 | 播放/暂停 |
| 右键小人 | 弹出菜单（播放、切歌、打开播放器、退出） |
| 右键托盘图标 | 快捷控制菜单 |
| 双击托盘图标 | 打开播放器窗口 |
| 右键播放列表歌曲 | 播放此曲 / 从列表移除 |

## 项目结构

```
EvernightPlaysMusic/
├── main.py              # 主程序入口
├── config_manager.py    # 配置读写
├── music_player.py      # 音乐播放引擎
├── pet_widget.py        # 桌面宠物窗口
├── player_window.py     # 播放器 UI 窗口
├── scanner.py           # 音频文件扫描
├── moon.gif             # 宠物素材
├── longmoon.webp        # 播放器背景图
├── moon.jpg             # 程序图标源文件
└── moon.ico             # 程序图标
```

## 依赖

- Python 3.12+
- PyQt5
- pygame-ce
- mutagen

## 配置

运行后会在 exe 同目录生成 `config.json`，记录：

- 已扫描的文件夹路径
- 播放列表
- 喜欢的歌曲
- 音量、播放模式
- 宠物窗口位置和大小

## 特殊包含内容

music文件夹下存放的是用于测试的一份作者自己的歌单喵，请按需使用喵~

