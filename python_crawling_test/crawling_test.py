import selenium.webdriver as webdriver
import time

#스크롤을 내린다.
def scroll_down(webdriver):
    webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# chrome 창을 띄우지 않고 크롤링
options = webdriver.ChromeOptions()
#options.add_argument('headless')
options.add_argument('disable-gpu')
driver = webdriver.Chrome('C:\\Users\\PSL\\Documents\\StyleView\\chromedriver.exe', options=options) # 설치경로입력

driver.implicitly_wait(15)

tag = 'hm_son7' # id
url = 'https://www.instagram.com/' + tag # id + instargram address

driver.get(url)
# image = KL4BH 한번에 12개 가져옴
totallist = driver.find_elements_by_class_name('g47SY')
pictures = driver.find_elements_by_class_name('FFVAD')
print("총 게시물의 갯수 :", totallist[0].text)
print("팔로워 :", totallist[1].text)
print(type(pictures))
print(len(pictures))
scroll_down(driver)

for n in pictures:
    print(n.get_attribute('src'))
driver.quit()
