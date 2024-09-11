from flask import Flask, render_template, request, send_file
import pdfkit
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin

app = Flask(__name__)

# Configure the path for pdfkit
pdfkit_config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Update this path

# Function to handle login for social media platforms
def login(platform, username, password):
    options = webdriver.ChromeOptions()
    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Update this path
    driver = webdriver.Chrome(options=options)
    
    try:
        if platform == 'twitter':
            driver.get("https://x.com/i/flow/login")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="text"]'))).send_keys(username)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]'))).click()
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))).send_keys(password)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button'))).click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label="Profile"]')))
        
        elif platform == 'facebook':
            driver.get("https://www.facebook.com/login")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))).send_keys(username)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="pass"]'))).send_keys(password)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, 'login'))).click()
        
        elif platform == 'instagram':
            driver.get("https://www.instagram.com/accounts/login/")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))).send_keys(username)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))).send_keys(password)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button'))).click()
        
        else:
            return "Unsupported platform."

        # Save the page content to a file
        with open('static/page.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        
        # Generate PDF from the saved HTML file
        pdfkit.from_file('static/page.html', 'static/output.pdf', configuration=pdfkit_config)
        return 'static/output.pdf'
    
    except (TimeoutException, NoSuchElementException) as e:
        return f"Error: {e}"
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
    
    pdf_path = login(platform, username, password)
    
    if pdf_path.startswith('static/'):
        return render_template('download.html')
    else:
        return f"Failed to generate PDF: {pdf_path}"

@app.route('/download')
def download():
    return send_file('static/output.pdf', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
