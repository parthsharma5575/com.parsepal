from flask import Flask, render_template, request, send_file
import pdfkit
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

app = Flask(__name__)

# Configure the path for pdfkit
pdfkit_config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Update this path

# Function to generate URLs based on the profile
def generate_urls(platform, profile):
    base_urls = {
        'instagram': {
            'followers': f"https://www.instagram.com/{profile}/followers/",
            'posts': f"https://www.instagram.com/{profile}/",
            'messages': f"https://www.instagram.com/direct/inbox/"
        },
        'twitter': {
            'followers': f"https://twitter.com/{profile}/followers",
            'posts': f"https://twitter.com/{profile}",
            'messages': f"https://twitter.com/messages"
        },
        'facebook': {
            'followers': f"https://www.facebook.com/{profile}/friends",
            'posts': f"https://www.facebook.com/{profile}",
            'messages': f"https://www.facebook.com/messages"
        }
    }
    return base_urls.get(platform, {})

# Function to handle login and screenshot generation
def login(platform, username, password, options):
    driver = webdriver.Chrome(options=options)
    
    try:
        if platform == 'instagram':
            driver.get("https://www.instagram.com/accounts/login/")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))).send_keys(username)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))).send_keys(password)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button'))).click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label="Profile"]')))
        
        elif platform == 'facebook':
            driver.get("https://www.facebook.com/login")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))).send_keys(username)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="pass"]'))).send_keys(password)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, 'login'))).click()
        
        elif platform == 'twitter':
            driver.get("https://x.com/i/flow/login")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="text"]'))).send_keys(username)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]'))).click()
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))).send_keys(password)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button'))).click()
        
        urls = generate_urls(platform, username)
        pdf_paths = []
        
        for content_type in ['followers', 'posts', 'messages']:
            if request.form.get(content_type):
                url = urls.get(content_type, '')
                if url:
                    print(f"Navigating to {url}")
                    driver.get(url)
                    print(f"Current URL: {driver.current_url}")
                    pdf_path = f'static/{content_type}.pdf'
                    try:
                        pdfkit.from_file(driver.current_url, pdf_path, configuration=pdfkit_config)
                        pdf_paths.append(f'{content_type}.pdf')
                    except Exception as e:
                        print(f"Failed to generate PDF for {content_type}: {e}")
                        pdf_paths.append(f"Error generating PDF for {content_type}")
        
        return pdf_paths

    except (TimeoutException, NoSuchElementException) as e:
        return [f"Error: {e}"]
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_route():
    platform = request.form['platform']
    username = request.form['username']
    password = request.form['password']
    
    options = webdriver.ChromeOptions()
    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Update this path

    pdf_paths = login(platform, username, password, options)
    
    if all(os.path.exists(f'static/{path}') for path in pdf_paths):
        return render_template('download.html', pdf_paths=pdf_paths)
    else:
        return f"Failed to generate PDFs: {', '.join(pdf_paths)}"

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'static/{filename}', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
