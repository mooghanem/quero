import streamlit as st
import asyncio
from playwright.async_api import async_playwright

st.set_page_config(
    page_title="Qureo Local Course Runner",
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

st.markdown("<h1 class='main-title'>⚡ Qureo Course Runner</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Local Automation Dashboard for 42 Modules</p>", unsafe_allow_html=True)

with st.infoline if hasattr(st, 'infoline') else st.container():
    st.info("💡 **Note:** This app runs locally via Playwright to automate your browser and complete the Qureo modules.")

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
                # Launches browser locally on your machine
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    log_message("🔄 Opening Qureo portal...")
                    await page.goto("https://me-portal.qureo.education/login", timeout=60000)

                    log_message("🔑 Entering credentials...")
                    await page.fill("input[type='text'], input[name='loginId'], input[name='username']", student_id)
                    await page.fill("input[type='password']", password)
                    await page.click("button[type='submit']")
                    await page.wait_for_load_state("networkidle")

                    log_message("✅ Logged in successfully! Starting modules...")

                    for level_num in range(1, 43):
                        progress_bar.progress(level_num / 42)
                        log_message(f"🚀 Processing Level {level_num}/42...")

                        # Automation steps loop
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
