import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5184/', { waitUntil: 'networkidle', timeout: 30000 });
    await page.screenshot({ path: 'login-page.png', fullPage: true });
    console.log('✅ Screenshot saved: login-page.png');
    
    // Check page title
    const title = await page.title();
    console.log(`Page title: ${title}`);
    
    // Check for government text
    const bodyText = await page.textContent('body');
    if (bodyText.includes('Government of Maharashtra')) {
      console.log('✅ Government of Maharashtra found');
    } else {
      console.log('❌ Government text not found. Body contains:', bodyText.slice(0, 200));
    }
    
    // Check for app name
    if (bodyText.includes('Samvaad')) {
      console.log('✅ Samvaad found');
    }
    
  } catch (e) {
    console.error('Error:', e.message);
  } finally {
    await browser.close();
  }
})();
