import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        
        await page.goto("http://localhost:8085/listone/")
        await page.wait_for_selector(".player-name-link", state="visible")
        
        # Click on the first player name
        first_player = page.locator(".player-name-link").first
        player_name = await first_player.inner_text()
        print(f"Clicking on player: {player_name}")
        await first_player.click()
        
        # Wait for modal to become active
        await page.wait_for_selector("#playerDetailModal.active", state="visible", timeout=5000)
        print("✓ Modal #playerDetailModal successfully opened!")
        
        # Take screenshot of the open modal
        await page.screenshot(path="scratch/player_modal_test.png")
        print("✓ Screenshot saved to scratch/player_modal_test.png")
        
        if errors:
            print("Errors detected:", errors)
        else:
            print("✓ No console errors!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
