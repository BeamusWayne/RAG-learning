#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
██████╗  █████╗ ████████╗███╗   ██╗███████╗████████╗
██╔══██╗██╔══██╗╚══██╔══╝████╗  ██║██╔════╝╚══██╔══╝
██████╔╝███████║   ██║   ██╔██╗ ██║█████╗     ██║
██╔══██╗██╔══██║   ██║   ██║╚██╗██║██╔══╝     ██║
██████╔╝██║  ██║   ██║   ██║ ╚████║███████╗   ██║
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝
BatNet v2.077 — 全球组网  |  Connecting...
"""

import sys
import time
import random
import math
import threading
import os

# ── ANSI 颜色 & 样式 ────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLINK   = "\033[5m"

    # 青绿色系 (Matrix / Cyberpunk)
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    DGREEN  = "\033[32m"
    LIME    = "\033[38;5;118m"
    TEAL    = "\033[38;5;51m"
    AQUA    = "\033[38;5;87m"

    # 黄/橙 (赛博朋克警告色)
    YELLOW  = "\033[93m"
    ORANGE  = "\033[38;5;214m"
    AMBER   = "\033[38;5;220m"

    # 紫红色
    MAGENTA = "\033[95m"
    PINK    = "\033[38;5;213m"
    VIOLET  = "\033[38;5;147m"

    # 白 / 灰
    WHITE   = "\033[97m"
    LGRAY   = "\033[37m"
    DGRAY   = "\033[90m"

    # 红
    RED     = "\033[91m"

    # 背景
    BG_BLACK= "\033[40m"

def clr(text, *codes):
    return "".join(codes) + text + C.RESET

# ── 终端尺寸 ────────────────────────────────────────────────────────────────
def term_size():
    try:
        cols, rows = os.get_terminal_size()
    except:
        cols, rows = 120, 40
    return cols, rows

# ── 清屏 / 定位 ─────────────────────────────────────────────────────────────
def clear():
    print("\033[2J\033[H", end="", flush=True)

def goto(row, col):
    print(f"\033[{row};{col}H", end="", flush=True)

def hide_cursor():
    print("\033[?25l", end="", flush=True)

def show_cursor():
    print("\033[?25h", end="", flush=True)

# ── 字符池 ──────────────────────────────────────────────────────────────────
MATRIX_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "アイウエオカキクケコサシスセソタチツテトナニヌネノ"
    "ハヒフヘホマミムメモヤユヨラリルレロワヲン"
    "!@#$%^&*()_+-=[]{}|;:,./<>?~`"
    "░▒▓█▄▀■□▪▫◆◇○●"
)

# ── 矩阵雨列 ────────────────────────────────────────────────────────────────
class RainColumn:
    def __init__(self, col, height):
        self.col    = col
        self.height = height
        self.head   = random.randint(-height, 0)
        self.speed  = random.uniform(0.3, 1.0)
        self.length = random.randint(6, 20)
        self.chars  = [random.choice(MATRIX_CHARS) for _ in range(height)]
        self.timer  = 0.0

    def update(self, dt):
        self.timer += dt
        if self.timer >= 1.0 / self.speed:
            self.timer = 0
            self.head += 1
            if self.head > self.height + self.length:
                self.head   = random.randint(-self.height // 2, 0)
                self.speed  = random.uniform(0.3, 1.0)
                self.length = random.randint(6, 20)
            # 随机变换部分字符
            for _ in range(random.randint(1, 3)):
                idx = random.randint(0, self.height - 1)
                self.chars[idx] = random.choice(MATRIX_CHARS)

    def render(self):
        """返回 (row, char, color_code) 列表"""
        cells = []
        for i in range(self.length):
            row = self.head - i
            if 0 <= row < self.height:
                if i == 0:
                    color = C.WHITE + C.BOLD
                elif i == 1:
                    color = C.AQUA + C.BOLD
                elif i < 4:
                    color = C.CYAN
                elif i < 8:
                    color = C.TEAL
                elif i < 12:
                    color = C.DGREEN
                else:
                    color = C.DGRAY + C.DIM
                cells.append((row, self.chars[row], color))
        return cells

# ── 节点数据 ─────────────────────────────────────────────────────────────────
NODES = [
    ("北京", "39.90°N", "116.40°E", "CN-BJ-01"),
    ("上海", "31.22°N", "121.47°E", "CN-SH-02"),
    ("纽约", "40.71°N", "74.00°W", "US-NY-03"),
    ("伦敦", "51.50°N", "0.12°W",  "UK-LD-04"),
    ("东京", "35.68°N", "139.69°E","JP-TK-05"),
    ("柏林", "52.52°N", "13.40°E", "DE-BL-06"),
    ("悉尼", "33.86°S", "151.20°E","AU-SY-07"),
    ("莫斯科","55.75°N", "37.61°E", "RU-MO-08"),
    ("迪拜", "25.20°N", "55.27°E", "AE-DB-09"),
    ("圣保罗","23.55°S", "46.63°W", "BR-SP-10"),
    ("新加坡","1.35°N",  "103.81°E","SG-SG-11"),
    ("开罗", "30.05°N", "31.23°E", "EG-CA-12"),
]

STATUS_POOL = [
    "HANDSHAKE",  "SYNC", "AUTH", "ENCRYPT",
    "ROUTING",    "RELAY", "PING", "ESTABLISH",
    "NEGOTIATE",  "SECURE", "VERIFIED", "ACTIVE",
]

PROTO_POOL = ["TLS1.3","AES-256","RSA-4096","ECDH","SHA-512","QUIC","WireGuard"]

# ── 配对任务 ─────────────────────────────────────────────────────────────────
class PairingTask:
    def __init__(self, src_idx, dst_idx):
        self.src    = NODES[src_idx]
        self.dst    = NODES[dst_idx]
        self.proto  = random.choice(PROTO_POOL)
        self.progress = 0.0
        self.speed  = random.uniform(0.4, 1.5)
        self.status = "HANDSHAKE"
        self.done   = False
        self.success= None
        self.age    = 0.0
        self.blink  = 0
        self.latency= random.randint(8, 320)
        self.key_bits= random.choice([128, 256, 512])

    def update(self, dt):
        if self.done:
            self.age += dt
            return
        self.progress = min(1.0, self.progress + dt * self.speed * 0.12)
        self.blink = (self.blink + 1) % 6
        # 根据进度切换状态
        p = self.progress
        if p < 0.15:  self.status = "HANDSHAKE"
        elif p < 0.30:self.status = "NEGOTIATE"
        elif p < 0.45:self.status = "AUTH"
        elif p < 0.60:self.status = "ENCRYPT"
        elif p < 0.75:self.status = "ROUTING"
        elif p < 0.90:self.status = "VERIFY"
        else:         self.status = "ESTABLISH"
        if self.progress >= 1.0:
            self.done    = True
            self.success = random.random() > 0.12
            self.status  = "CONNECTED" if self.success else "FAILED"

# ── 日志消息池 ───────────────────────────────────────────────────────────────
LOG_TEMPLATES = [
    lambda n: f"[NODE] {n[3]} 上线 — IP {random_ip()}",
    lambda n: f"[SEC]  密钥交换完成  {n[3]} ◀▶ {random_node()[3]}",
    lambda n: f"[NET]  路由优化  跳数↓{random.randint(1,4)}  延迟 {random.randint(5,80)}ms",
    lambda n: f"[PKT]  封包校验  {random.randint(1000,9999)} frames / {random.randint(1,99)} MB",
    lambda n: f"[AUTH] 证书验证  {random.choice(PROTO_POOL)} OK",
    lambda n: f"[ERR]  重试 #{random.randint(1,5)}  节点 {random_node()[3]}",
    lambda n: f"[OK]   隧道建立  {n[3]} ←→ {random_node()[3]}  ✓",
    lambda n: f"[SYN]  时钟同步  偏移 {random.randint(0,9)}.{random.randint(0,999):03d} ms",
]

def random_ip():
    return ".".join(str(random.randint(1,254)) for _ in range(4))

def random_node():
    return random.choice(NODES)

# ── 进度条 ───────────────────────────────────────────────────────────────────
def progress_bar(p, width=20):
    filled = int(p * width)
    bar    = "█" * filled + "░" * (width - filled)
    pct    = int(p * 100)
    if p >= 1.0:
        return clr(f"[{bar}]", C.GREEN), clr(f"{pct:3d}%", C.GREEN + C.BOLD)
    elif p > 0.6:
        return clr(f"[{bar}]", C.CYAN), clr(f"{pct:3d}%", C.CYAN)
    else:
        return clr(f"[{bar}]", C.TEAL), clr(f"{pct:3d}%", C.AMBER)

# ── 主渲染器 ─────────────────────────────────────────────────────────────────
class BatNet:
    def __init__(self):
        self.cols, self.rows = term_size()
        self.rain   = [RainColumn(c, self.rows) for c in range(self.cols)]
        self.tasks  : list[PairingTask] = []
        self.logs   : list[str] = []
        self.tick   = 0
        self.elapsed= 0.0
        self.total_connected = 0
        self.total_failed    = 0
        self._spawn_tasks()

    def _spawn_tasks(self):
        indices = list(range(len(NODES)))
        random.shuffle(indices)
        # 生成若干配对
        for i in range(0, min(10, len(indices)-1), 2):
            self.tasks.append(PairingTask(indices[i], indices[i+1]))

    def _add_log(self, msg):
        ts  = f"\033[90m[{self.elapsed:07.2f}s]\033[0m "
        self.logs.append(ts + msg)
        if len(self.logs) > 200:
            self.logs.pop(0)

    # ── 标题区 ──────────────────────────────────────────────────────────────
    def _render_header(self):
        cols = self.cols
        lines = []

        # 顶部装饰线
        lines.append(clr("╔" + "═" * (cols - 2) + "╗", C.CYAN + C.BOLD))

        title = "██████╗  █████╗ ████████╗███╗   ██╗███████╗████████╗"
        sub   = "全球组网  GLOBAL MESH NETWORK  v2.077"
        conn  = f"[ Connecting... ]  节点在线: {len(NODES)}  已配对: {self.total_connected}  失败: {self.total_failed}"

        def center_line(text, color=""):
            raw = text  # may contain ANSI; calc visible len naively
            visible = len(text)  # ASCII-safe here
            pad = max(0, (cols - visible - 2) // 2)
            return clr("║", C.CYAN + C.BOLD) + " " * pad + (color + text + C.RESET) + " " * (cols - 2 - pad - visible) + clr("║", C.CYAN + C.BOLD)

        # ASCII title (两行)
        bat1 = "██████╗  █████╗ ████████╗███╗   ██╗███████╗████████╗"
        bat2 = "██╔══██╗██╔══██╗╚══██╔══╝████╗  ██║██╔════╝╚══██╔══╝"
        bat3 = "██████╔╝███████║   ██║   ██╔██╗ ██║█████╗     ██║   "
        bat4 = "██╔══██╗██╔══██║   ██║   ██║╚██╗██║██╔══╝     ██║   "
        bat5 = "██████╔╝██║  ██║   ██║   ██║ ╚████║███████╗   ██║   "
        bat6 = "╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝   "
        sub_cn = "B A T N E T  —  全球组网"

        for ln in [bat1, bat2, bat3, bat4, bat5, bat6]:
            lines.append(center_line(ln, C.CYAN + C.BOLD))

        lines.append(clr("║" + " " * (cols - 2) + "║", C.CYAN + C.BOLD))
        lines.append(center_line(sub_cn, C.AMBER + C.BOLD))

        # 副标题 + 连接状态（固定颜色）
        lines.append(center_line("◈  Connecting  ◈", C.PINK + C.BOLD))
        lines.append(center_line(conn, C.LGRAY))
        lines.append(clr("╠" + "═" * (cols - 2) + "╣", C.CYAN + C.BOLD))

        return lines

    # ── 配对面板 ─────────────────────────────────────────────────────────────
    def _render_pairs(self):
        cols  = self.cols
        lines = []

        # 分两列显示
        panel_w = (cols - 3) // 2

        active = [t for t in self.tasks if not t.done or t.age < 2.5][:8]

        # 标题行
        head = clr(" 配对任务  PAIRING MATRIX", C.AMBER + C.BOLD)
        lines.append(clr("║", C.CYAN + C.BOLD) + head + " " * (cols - 2 - 22) + clr("║", C.CYAN + C.BOLD))

        for i in range(0, len(active), 2):
            left  = active[i]   if i   < len(active) else None
            right = active[i+1] if i+1 < len(active) else None

            def task_line(t, w):
                if t is None:
                    return " " * w
                bar, pct = progress_bar(t.progress, 16)
                src = t.src[0][:3]
                dst = t.dst[0][:3]
                arrow = clr("──►", C.TEAL) if not t.done else (clr("══✓", C.GREEN) if t.success else clr("══✗", C.RED))
                if t.done and t.success:
                    sc = C.GREEN
                elif t.done:
                    sc = C.RED + C.BOLD
                else:
                    sc = C.CYAN

                status_str = clr(f"[{t.status:<9}]", sc)
                proto_str  = clr(t.proto, C.VIOLET + C.DIM)

                line = f" {clr(src, C.AMBER+C.BOLD)}{arrow}{clr(dst, C.AMBER+C.BOLD)} {bar}{pct} {status_str} {proto_str} "
                # 粗略截断到宽度
                visible = len(src) + len(dst) + 4 + 22 + 12 + len(t.status) + 12 + len(t.proto) + 4
                return line + " " * max(0, w - visible)

            ll = task_line(left,  panel_w)
            lr = task_line(right, panel_w)
            sep = clr("│", C.DGRAY)
            row = clr("║", C.CYAN + C.BOLD) + ll + sep + lr + clr("║", C.CYAN + C.BOLD)
            lines.append(row)

        return lines

    # ── 全球节点表 ────────────────────────────────────────────────────────────
    def _render_nodes(self):
        cols  = self.cols
        lines = []
        lines.append(clr("╠" + "═" * (cols - 2) + "╣", C.CYAN + C.BOLD))
        head = clr(" 全球节点状态  NODE STATUS TABLE", C.LIME + C.BOLD)
        lines.append(clr("║", C.CYAN + C.BOLD) + head + " " * (cols - 2 - 28) + clr("║", C.CYAN + C.BOLD))

        col_nodes = (cols - 3) // 3
        for row_i in range(0, len(NODES), 3):
            row_parts = []
            for j in range(3):
                idx = row_i + j
                if idx < len(NODES):
                    n = NODES[idx]
                    # 随机脉冲
                    pulse = random.random()
                    if pulse > 0.97:
                        sc = C.RED
                        tag= "◉ WARN "
                    elif pulse > 0.90:
                        sc = C.AMBER
                        tag= "◎ SYNC "
                    else:
                        sc = C.GREEN
                        tag= "● LIVE "
                    nm  = clr(n[0], C.WHITE + C.BOLD)
                    id_ = clr(n[3], C.DGRAY)
                    lat = clr(f"{random.randint(5,99):2d}ms", C.TEAL)
                    cell= f" {clr(tag, sc)}{nm} {id_} {lat} "
                else:
                    cell = " " * col_nodes
                row_parts.append(cell)
            # 拼三列
            sep = clr("│", C.DGRAY)
            ln = clr("║", C.CYAN + C.BOLD) + row_parts[0] + sep + row_parts[1] + sep + (row_parts[2] if len(row_parts) > 2 else "") + clr("║", C.CYAN + C.BOLD)
            lines.append(ln)

        return lines

    # ── 日志滚动区 ────────────────────────────────────────────────────────────
    def _render_logs(self, n_lines=5):
        cols  = self.cols
        lines = []
        lines.append(clr("╠" + "═" * (cols - 2) + "╣", C.CYAN + C.BOLD))
        head = clr(" 系统日志  SYSTEM LOG", C.VIOLET + C.BOLD)
        lines.append(clr("║", C.CYAN + C.BOLD) + head + " " * (cols - 2 - 20) + clr("║", C.CYAN + C.BOLD))

        show = self.logs[-(n_lines):]
        for lg in show:
            # 截断到终端宽度
            visible_len = min(len(lg), cols - 4)
            padded = lg[:visible_len] + " " * max(0, cols - 4 - visible_len)
            lines.append(clr("║", C.CYAN + C.BOLD) + " " + padded + " " + clr("║", C.CYAN + C.BOLD))

        return lines

    # ── 底部状态栏 ────────────────────────────────────────────────────────────
    def _render_footer(self):
        cols = self.cols
        enc  = random.choice(PROTO_POOL)
        bw   = f"{random.uniform(0.5, 9.9):.1f} GB/s"
        pkt  = f"{random.randint(100000, 999999):,} pkt/s"
        uptime = f"{int(self.elapsed // 60):02d}:{int(self.elapsed % 60):02d}"
        status_line = (
            f" ⚡ 上行 {clr(bw, C.LIME+C.BOLD)}  "
            f"📦 吞吐 {clr(pkt, C.CYAN)}  "
            f"🔐 加密 {clr(enc, C.VIOLET)}  "
            f"⏱  {clr(uptime, C.AMBER)}  "
            f"BATNET © 2077 "
        )
        ln = clr("╠" + "═" * (cols - 2) + "╣", C.CYAN + C.BOLD)
        foot = clr("╚" + "═" * (cols - 2) + "╝", C.CYAN + C.BOLD)
        return [ln, clr("║", C.CYAN + C.BOLD) + status_line + clr("║", C.CYAN + C.BOLD), foot]

    # ── 矩阵雨背景层（只在空行绘制少量字符） ───────────────────────────────
    def _tick_rain(self, dt):
        for col in self.rain:
            col.update(dt)

    # ── 主循环 ────────────────────────────────────────────────────────────────
    def run(self):
        hide_cursor()
        last_t = time.time()
        log_timer = 0.0

        try:
            while True:
                now  = time.time()
                dt   = now - last_t
                last_t = now
                self.elapsed += dt
                self.tick    += 1

                # 更新矩阵雨
                self._tick_rain(dt)

                # 更新任务
                for t in self.tasks:
                    t.update(dt)
                    if t.done and not hasattr(t, "_counted"):
                        t._counted = True
                        if t.success:
                            self.total_connected += 1
                        else:
                            self.total_failed += 1

                # 清理完成的旧任务，补充新任务
                self.tasks = [t for t in self.tasks if not t.done or t.age < 3.0]
                while len(self.tasks) < 8:
                    a, b = random.sample(range(len(NODES)), 2)
                    self.tasks.append(PairingTask(a, b))

                # 产生日志
                log_timer += dt
                if log_timer > random.uniform(0.3, 0.8):
                    log_timer = 0
                    n = random.choice(NODES)
                    tmpl = random.choice(LOG_TEMPLATES)
                    color = random.choice([C.GREEN, C.CYAN, C.AMBER, C.VIOLET, C.LIME, C.RED])
                    self._add_log(color + tmpl(n) + C.RESET)

                # 渲染
                self._draw()

                time.sleep(0.08)   # ~12 fps

        except KeyboardInterrupt:
            pass
        finally:
            show_cursor()
            clear()
            print(clr("\n  BatNet 已断开连接。  Disconnected.\n", C.CYAN + C.BOLD))

    def _draw(self):
        cols, rows = self.cols, self.rows

        # 先绘制矩阵雨（直接写到屏幕，使用绝对定位）
        # 收集所有内容行数，在雨中留出主面板区域
        buf = []

        header_lines = self._render_header()
        pair_lines   = self._render_pairs()
        node_lines   = self._render_nodes()
        log_lines    = self._render_logs(5)
        foot_lines   = self._render_footer()

        all_lines = header_lines + pair_lines + node_lines + log_lines + foot_lines

        # 用矩阵雨填充背景剩余行
        rain_cells: dict[tuple[int,int], tuple[str,str]] = {}
        panel_height = len(all_lines)

        for rc in self.rain:
            for (row, ch, color) in rc.render():
                if row >= panel_height:  # 只在面板下方绘制雨
                    rain_cells[(row, rc.col)] = (ch, color)

        # 构建完整画面
        output = ["\033[H"]  # 跳到左上角，不清屏（减少闪烁）

        for i, line in enumerate(all_lines):
            output.append(line + "\033[K\n")   # 清到行尾

        # 绘制矩阵雨行
        for row in range(panel_height, rows - 1):
            line_chars = []
            for col in range(cols):
                if (row, col) in rain_cells:
                    ch, color = rain_cells[(row, col)]
                    line_chars.append(color + ch + C.RESET)
                else:
                    # 随机散落的暗字符（背景噪声）
                    if random.random() < 0.003:
                        line_chars.append(C.DGRAY + C.DIM + random.choice("01") + C.RESET)
                    else:
                        line_chars.append(" ")
            output.append("".join(line_chars) + "\n")

        sys.stdout.write("".join(output))
        sys.stdout.flush()


# ── 入口 ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # 检查终端支持
    if sys.platform == "win32":
        os.system("color")   # 开启 ANSI（Windows 10+）

    app = BatNet()
    app.run()