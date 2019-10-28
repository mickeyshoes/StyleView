import selenium.webdriver as webdriver


# chrome 창을 띄우지 않고 크롤링
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('disable-gpu')
driver = webdriver.Chrome('C:\\Users\\PSL\\Documents\\StyleView\\chromedriver.exe', options=options) # 설치경로입력

driver.implicitly_wait(15)

url = 'https://www.instagram.com/hm_son7/?hl=ko'

driver.get(url)
totalcount = driver.find_element_by_class_name('g47SY').text
print("총 게시물의 갯수 :", totalcount)

driver.quit()
