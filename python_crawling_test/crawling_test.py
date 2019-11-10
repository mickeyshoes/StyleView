import selenium.webdriver as webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import urllib.request
import os

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

ID = input('ID')
PW = input('PW')

driver.get(url)
totallist = driver.find_elements_by_class_name('g47SY')
profile = driver.find_element_by_class_name('_6q-tv')
print("프로필 사진:", profile.get_attribute('src'))
print("총 게시물의 갯수 :", totallist[0].text)
print("팔로워 :", totallist[1].text)

photo_list = []
total_count = int(totallist[0].text)
# if total_count > 101:
#     total_count = 100

# 크롤링 중 로그인 문제로 인한 로그인 선행
time.sleep(1)
driver.find_element_by_xpath('/html/body/span/section/nav/div[2]/div/div/div[3]/div/span/a[1]/button').click()
driver.find_elements_by_name('username')[0].send_keys(ID)
driver.find_elements_by_name('password')[0].send_keys(PW)
time.sleep(2)
driver.find_element_by_xpath('/html/body/span/section/main/div/article/div/div[1]/div/form/div[4]/button').submit()


#이미지 크롤링 시작
while True:

    pictures = driver.find_elements_by_class_name('FFVAD')
    print(len(pictures))
    #현재의 스크롤 높이를 가져옴
    last_height = driver.execute_script("return document.body.scrollHeight")

    for n in pictures:
        temp = {}
        temp['src'] = n.get_attribute('src')
        #pic_list.append(temp)

        if n in photo_list:
            pass

        else:
            photo_list.append(temp)

    scroll_down(driver)

    #스크롤을 내린 높이를 가져옴
    scrolled_height = driver.execute_script("return document.body.scrollHeight")

    print(len(photo_list))

    if scrolled_height == last_height:
        break
    
# dictionary의 key 값은 중복이 되지 않는 점을 이용하여 중복 제거
tmp_dict = {}
tmp_list = []

for n in photo_list:
    tmp_dict[n['src']] = n['src']
    
tmp_list = tmp_dict.values()

save_path = 'C:\\Users\\PSL\\Documents\\StyleView\\python_crawling_test\\'+tag+'\\'

if not os.path.isdir(save_path):
    os.makedirs(save_path)

# for i, n in enumerate(photo_list):
#     urllib.request.urlretrieve(n['src'], save_path + tag + str(i)+'.jpg')

index = 0

for n in tmp_list:
    urllib.request.urlretrieve(n, save_path + tag + '_' +str(index)+'.jpg')
    index+=1

driver.quit()