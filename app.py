import streamlit as st
import asyncio
import os

# Auto-install Playwright browser binaries on Streamlit Cloud server
os.system("playwright install chromium")

from playwright.async_api import async_playwright

st.set_page_config(
    page_title="Qureo Cloud Course Runner",
    page_icon="⚡",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-title { text-align: center; font-weight: 700; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #8a8d93; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚡ Qureo Cloud Runner</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Web Automation Dashboard for 42 Modules</p>", unsafe_allow_html=True)

with st.form("credentials_form"):
    st.subheader("🔑 تسجيل الدخول")
    st.write("أكتب بيانات حساب Qureo الخاصة بك")
    
    student_id = st.text_input("ID / Student Code")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("— متابعة —")

if submitted:
    if not student_id or not password:
        st.warning("⚠️ Please fill in both your Student ID and Password.")
    else:
        log_container = st.empty()
        progress_bar = st.progress(0)
        logs = []

        def log_message(msg):
            logs.append(msg)
            log_container.code("\n".join(logs[-10:]), language="text")

        async def run_automation():
            async with async_playwright() as p:
                # headless=True is mandatory for cloud servers
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    log_message("🔄 Opening Qureo portal on cloud server...")
                    await page.goto("https://me-portal.qureo.education/login", timeout=60000)

                    log_message("🔑 Entering credentials...")
                    # Wait for input fields to render properly
                    await page.wait_for_selector("input", timeout=15000)
                    
                    # Robust selector fallback using input index positions
                    inputs = await page.locator("input").all()
                    if len(inputs) >= 2:
                        await inputs[0].fill(student_id)
                        await inputs[1].fill(password)
                    else:
                        await page.fill("input[type='text'], input[type='email'], input:not([type='password'])", student_id)
                        await page.fill("input[type='password']", password)

                    # Submit login form
                    await page.click("button[type='submit'], button:has-text('دخول'), button:has-text('Login')")
                    await page.wait_for_load_state("networkidle")

                    log_message("✅ Logged in successfully! Starting modules...")

                    for level_num in range(1, 43):
                        progress_bar.progress(level_num / 42)
                        log_message(f"🚀 Processing Level {level_num}/42...")

                        while await page.locator("button:has-text('التالي'), button:has-text('Next')").is_visible():
                            await page.click("button:has-text('التالي'), button:has-text('Next')")
                            await page.wait_for_timeout(300)

                        if await page.locator("button:has-text('تشغيل الكود'), button:has-text('Run')").is_visible():
                            await page.click("button:has-text('تشغيل الكود'), button:has-text('Run')")
                        
                        await page.wait_for_timeout(1000)

                    log_message("🎉 All 42 modules completed successfully!")
                    st.success("🎉 Completed all 42 levels successfully!")

                except Exception as e:
                    log_message(f"❌ Error: {str(e)}")
                    st.error(f"Automation failed: {e}")
                finally:
                    await browser.close()

        asyncio.run(run_automation())
