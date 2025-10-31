from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os, time
from playwright.sync_api import sync_playwright, TimeoutError


app = FastAPI()


os.makedirs("screenshots", exist_ok=True)
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")


@app.get('/playwright')
def playwright_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url_names = []

        print("Opening Amazon")
        # Connecting to Amazon with a timeout error in case Amazon is down or taking too long to load
        try:
            page.goto('https://www.amazon.com/', timeout=10000)
        except TimeoutError:
            return JSONResponse({"status": "error", "message": "Timeout loading page"})
            # browser.close()
            # return

        # There is sometimes a captcha that I am pressing if it shows up when trying to visit Amazon
        if page.get_by_role('button').get_by_text('Continue Shopping').is_visible():
            page.get_by_role('button').get_by_text('Continue Shopping').click()
        
        # Taking a screenshot as evidence of reaching the landing page
        print('Amazon page loaded successfully')
        screenshot_path = 'screenshots/landing_page.png'
        url_names.append(screenshot_path)
        page.screenshot(path=screenshot_path)
        

        print('Searching for a blue shirt')

        # There are two versions of the landing page I am seeing, one where the search bar has the 'Search Amazon' Placeholder text 
        # and an icon button and one where the search bar is empty with a button that says 'Go'
        if page.locator("label:has-text('Search Amazon')").count() > 0:
            # 'Search Amazon' Placeholder'
            page.get_by_placeholder('Search Amazon').fill('blue shirt')
            page.click('#nav-search-submit-button')
        
        else:
            # No Placeholder
            page.fill('#nav-bb-search', 'blue shirt')
            page.click('input.nav-bb-button')


        # Taking a screenshot as evidence of executing the search
        page.wait_for_selector("[data-component-type='s-search-result']")
        screenshot_path = 'screenshots/search_results.png'
        url_names.append(screenshot_path)
        page.screenshot(path=screenshot_path)


        print('Selecting a shirt under $5')
        page_number = 1
        
        # This loop handles filtering all the results that show up on each page
        while True:
            print(f"Searching page {page_number}...")
            page.wait_for_selector("[data-component-type='s-search-result']", timeout=10000)
                
            # Scroll to load all items first
            last_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.mouse.wheel(0, 2000)  # scroll down
                time.sleep(1)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            # Use JavaScript to collect all results on the current page (was a bit more reliable than emulating this same scrape with playwright code)
            items_data = page.evaluate("""
                () => {
                    const items = document.querySelectorAll("[data-component-type='s-search-result']");
                    return Array.from(items).map((item, index) => {
                        const priceElement = item.querySelector('span.a-price span.a-offscreen');
                        return {
                            dataIndex: item.getAttribute('data-index'),
                            priceText: priceElement ? priceElement.textContent : null,
                        };
                    });
                }
            """)
                
            
            
            # Actually check the prices to see if we found a hit on our search
            found = False
            for item in items_data:
                if item['priceText']:
                    try:
                        print(item['priceText'])
                        price = float(item['priceText'].strip().replace('$', ''))
                        if price < 5:
                            print(f"Found shirt under $5: {item['priceText']}")
                            # Click the actual item
                            selected_shirt = page.locator(f'[data-component-type="s-search-result"][data-index="{item["dataIndex"]}"] img.s-image').first
                            selected_shirt.scroll_into_view_if_needed()
                            selected_shirt.wait_for(state='visible', timeout=5000)
                            selected_shirt.click()                           
                            found = True
                            break
                    except Exception as e:
                        print(f"Error processing item {item}: {str(e)}")
                        continue
                else:
                    continue
            
            # Allow the code to progress to handle adding the shirt to the cart since we clicked the shirt in the for loop
            if found:
                break

            # Check for next page
            next_button = page.locator('a.s-pagination-item.s-pagination-next')
            if next_button.count() > 0 and next_button.is_enabled():
                print("Moving to next page...")
                next_button.click()
                page.wait_for_selector("div[role='listitem']", timeout=10000)
                page_number += 1
            else:
                return JSONResponse({'status': 'error', 'message': 'No more pages available - no blue shirts found under $5'})
                # browser.close()
                # return
        
       # Taking a screenshot as evidence of ending up on the product's page
        print('shirt selected')
        page.wait_for_selector("#productTitle", state="visible")
        screenshot_path = 'screenshots/shirt_selected.png'
        url_names.append(screenshot_path)
        page.screenshot(path=screenshot_path)

        # Adding it to cart and then clicking on the cart to prove it is in the cart
        button = page.locator("input#add-to-cart-button")
        button.click()
        print('shirt added to cart')

        cart_button = page.locator('a#nav-cart')
        cart_button.click()

        # Taking a screenshot as evidence of the product ending up in the cart
        page.wait_for_selector('#sc-active-items-header', state='visible')
        screenshot_path = 'screenshots/cart_confirm.png'
        url_names.append(screenshot_path)
        page.screenshot(path=screenshot_path)
        browser.close()
    
    # Serving the screenshots using the StaticFiles middleware
    final_urls = [f"/{f}" for f in url_names]
    return JSONResponse({"status": "success", "screenshots": final_urls})




@app.get("/")
async def root():
    return {"message": "API for task 3. Visit /playwright endpoint to enable the playwright driver"}