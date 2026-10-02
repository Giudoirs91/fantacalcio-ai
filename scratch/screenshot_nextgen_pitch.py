import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1680, 'height': 1050})
        page = await context.new_page()
        
        print("Navigating to http://localhost:8085/probabili-formazioni/ ...")
        await page.goto("http://localhost:8085/probabili-formazioni/", wait_until="networkidle")
        
        # Select Inter
        print("Selecting Inter...")
        await page.evaluate("renderPitchTeam('Inter')")
        await page.wait_for_timeout(1500)
        
        # Screenshot the pitch container wrapper
        pitch_wrapper = page.locator(".pitch-container-wrapper")
        out_path = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\713f4e0e-2be2-453f-827d-8247c251babb\nextgen_pitch_inter.png"
        await pitch_wrapper.screenshot(path=out_path)
        print(f"Pitch wrapper screenshot saved to {out_path}")
        
        # Also full page screenshot
        full_path = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\713f4e0e-2be2-453f-827d-8247c251babb\nextgen_probabili_formazioni_full.png"
        await page.screenshot(path=full_path, full_page=False)
        print(f"Full page screenshot saved to {full_path}")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
