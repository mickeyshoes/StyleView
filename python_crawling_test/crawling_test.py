import selenium.webdriver as webdriver
import time
import urllib.request
import os
#from bs4 import BeautifulSoup


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

tag = 'sjkuksee' # id
url = 'https://www.instagram.com/' + tag # id + instargram address

ID = input('ID')
PW = input('PW')

driver.get(url)
#soup = BeautifulSoup("""<body class ="" style="overflow: hidden;">""", "lxml")
#soup.find("body")['style'] = 'style = "overflow: auto;"'
# image = KL4BH 한번에 12개 가져옴
totallist = driver.find_elements_by_class_name('g47SY')
profile = driver.find_element_by_class_name('_6q-tv')
print("프로필 사진:", profile.get_attribute('src'))
print("총 게시물의 갯수 :", totallist[0].text)
print("팔로워 :", totallist[1].text)

'''pictures = driver.find_elements_by_class_name('FFVAD')
print(type(pictures))
print(len(pictures))
scroll_down(driver)

for n in pictures:


    print(n.get_attribute('src'))'''

photo_list = []
total_count = int(totallist[0].text)
overlap_count = 0
if total_count > 101:
    total_count = 200

    time.sleep(1)
    driver.find_element_by_xpath('/html/body/span/section/nav/div[2]/div/div/div[3]/div/span/a[1]/button').click()
    driver.find_elements_by_name('username')[0].send_keys(ID)
    driver.find_elements_by_name('password')[0].send_keys(PW)
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/span/section/main/div/article/div/div[1]/div/form/div[4]/button').submit()


while True:

    '''if overlap_count == 0 :
        for n in range(3):'''


    pictures = driver.find_elements_by_class_name('FFVAD')
    print(len(pictures))
    #pic_list = []

    for n in pictures:
        temp = {}
        temp['src'] = n.get_attribute('src')
        #pic_list.append(temp)

        if n in photo_list:
            pass

        else:
            photo_list.append(temp)

    

    scroll_down(driver)

    print(len(photo_list))


    if len(photo_list) > total_count:
        break

# for n in photo_list:
#     print(n['src'])

print(len(photo_list))
# print(photo_list)

tmpd = {}
tmpl = []

for n in photo_list:
    tmpd[n['src']] = n['src']
    
tmpl = tmpd.values()

save_path = 'C:\\Users\\PSL\\Documents\\StyleView\\python_crawling_test\\'+tag+'\\'

if not os.path.isdir(save_path):
    os.makedirs(save_path)

# for i, n in enumerate(photo_list):
#     urllib.request.urlretrieve(n['src'], save_path + tag + str(i)+'.jpg')

index = 0

print(tmpl)

for n in tmpl:
    urllib.request.urlretrieve(n, save_path + tag + str(index)+'.jpg')
    index+=1

driver.quit()
