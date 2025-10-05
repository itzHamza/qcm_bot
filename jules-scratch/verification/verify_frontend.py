from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:5000/")
    page.set_input_files('input[type="file"]', 'jules-scratch/verification/dummy.pdf')
    page.click('button[type="submit"]')
    page.wait_for_selector("text=Conversion successful!")
    page.screenshot(path="jules-scratch/verification/verification.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
