"""
Plain login helper for GP register automation.

This file intentionally stays readable: it only opens/connects Chrome, checks
login state, and leaves the browser running for the protected submitter. By
default it does not wait for manual login; pass --wait to keep polling.
"""

import argparse
import io
import os
import subprocess
import sys
import time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_URL = "https://gp.itcm.cn"
CDP_PORT = 9222
DEFAULT_OUTDIR = os.path.dirname(os.path.abspath(__file__))
CDP_RETRY_MAX = 5
CDP_RETRY_INTERVAL = 2
LOGIN_TIMEOUT = 180


def log(msg: str):
    print(msg, flush=True)


def _connect_or_launch(playwright, outdir: str, cdp_port: int):
    cdp_url = f"http://127.0.0.1:{cdp_port}"
    try:
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        log(f">>> 已连接到 Chrome: {cdp_url}")
        return browser
    except Exception:
        pass

    user_data_dir = os.path.join(outdir, ".gp_browser_profile")
    os.makedirs(user_data_dir, exist_ok=True)

    log(">>> 启动 Chrome（登录状态会保存在本地浏览器配置中）...")
    chrome = playwright.chromium.executable_path
    subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--start-maximized",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x00000008 if sys.platform == "win32" else 0,
    )

    for attempt in range(CDP_RETRY_MAX):
        time.sleep(CDP_RETRY_INTERVAL)
        try:
            browser = playwright.chromium.connect_over_cdp(cdp_url)
            log(f">>> Chrome 已就绪: {cdp_url}")
            return browser
        except Exception:
            if attempt == CDP_RETRY_MAX - 1:
                raise


def _get_page(browser):
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    pages = ctx.pages
    if pages:
        page = pages[0]
        page.bring_to_front()
    else:
        page = ctx.new_page()
    return page


def _needs_login(page) -> bool:
    return "login" in page.url.lower() or page.locator('input[type="password"]').count() > 0


def _check_logged_in(page) -> bool:
    if _needs_login(page):
        return False
    sidebar = page.locator("#LAY-system-side-menu")
    has_menu = page.get_by_text("登记手册").count() > 0
    return sidebar.count() > 0 or has_menu


def _wait_for_login(page, outdir: str, timeout: int):
    signal_path = os.path.join(outdir, "gp_continue.txt")
    waited = 0
    log(">>> 请在打开的浏览器里手动登录 gp.itcm.cn")
    log(">>> 登录后可等待自动检测，或在输出目录创建 gp_continue.txt 立即重检")
    while waited < timeout:
        if os.path.exists(signal_path):
            try:
                os.remove(signal_path)
            except OSError:
                pass
            time.sleep(0.5)
            if _check_logged_in(page):
                log(">>> [OK] 登录验证通过（gp_continue.txt 信号）")
                return
        if _check_logged_in(page):
            log(">>> [OK] 登录验证通过")
            return
        time.sleep(2)
        waited += 2
    raise TimeoutError(f"登录等待超时（{timeout // 60} 分钟）")

def ensure_login(outdir: str = None, cdp_port: int = CDP_PORT, timeout: int = LOGIN_TIMEOUT, wait: bool = False) -> bool:
    outdir = outdir or DEFAULT_OUTDIR
    os.makedirs(outdir, exist_ok=True)

    from playwright.sync_api import sync_playwright

    p = sync_playwright().start()
    try:
        browser = _connect_or_launch(p, outdir, cdp_port)
        page = _get_page(browser)

        log(f">>> Navigate to {BASE_URL}")
        page.goto(BASE_URL, timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1.5)

        if _needs_login(page) or not _check_logged_in(page):
            log("\n============================================")
            log(">>> [LOGIN_REQUIRED] Please manually log in to gp.itcm.cn in the opened Chrome window.")
            log(">>> After login is complete, tell the AI to continue. It should run gp_login.py again to verify.")
            log(">>> This script does not submit any records.")
            log("============================================")
            if wait:
                _wait_for_login(page, outdir, timeout)
            else:
                return False

        log(">>> [LOGIN_READY] Login is ready. Keep Chrome open, then run gp_playwright.py.")
        return True
    finally:
        # Do not close Chrome. Only detach the Playwright controller.
        try:
            p.stop()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="GP 登录准备脚本（明文，不包含提交逻辑）")
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR, help=f"输出目录 (默认: {DEFAULT_OUTDIR})")
    parser.add_argument("--port", type=int, default=CDP_PORT, help=f"Chrome CDP 端口 (默认: {CDP_PORT})")
    parser.add_argument("--timeout", type=int, default=LOGIN_TIMEOUT, help="Login wait seconds, only used with --wait (default: 180)")
    parser.add_argument("--wait", action="store_true", help="Old behavior: keep polling when manual login is required")
    args = parser.parse_args()
    ensure_login(outdir=args.outdir, cdp_port=args.port, timeout=args.timeout, wait=args.wait)


if __name__ == "__main__":
    main()
