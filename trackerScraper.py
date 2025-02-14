import pyautogui
import time


print("Starting the scraping")
print("Open the match in a new window on the main screen")
print("Move mouse onto first round")
filenamePrefix = input("Please enter the map followed by date month year and time")

input()


pyautogui.click()
pyautogui.keyDown('ctrl')
pyautogui.press('s')
pyautogui.keyUp('ctrl')

time.sleep(2)

pyautogui.press('backspace')
roundCount = 1
pyautogui.write(filenamePrefix + f"-Round{roundCount}")