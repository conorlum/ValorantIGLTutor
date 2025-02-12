import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start with the browser maximized

# Use WebDriverManager to get the path to the latest version of ChromeDriver
driver_path = ChromeDriverManager().install()

# Create a Service object
service = Service(driver_path)

# Start the Chrome browser
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the desired website
driver.get('https://tracker.gg/valorant/profile/riot/NPrightdolphin%23NA1/overview')  # Replace with your desired URL

input("enter:")