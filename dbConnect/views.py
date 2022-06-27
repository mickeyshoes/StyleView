from django.shortcuts import render
from django.http import HttpResponse
import pymysql
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import json
import selenium.webdriver as webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import urllib.request
import os
from selenium.webdriver.common.keys import Keys
from django.views.decorators.csrf import csrf_exempt



# Create your views here.

@csrf_exempt
def test_web(request):
    return HttpResponse("Hello 418!")

# instagram id를 저장한 table에 접근하여 아이디와 비밀번호를 얻음
@csrf_exempt
def print_insta_ID(request):
    insta_id = request.POST.get('insta_id','')

    con = pymysql.connect(host='localhost', user=os.environ.get('MYSQL_USER'), password =os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
    curs = con.cursor(pymysql.cursors.DictCursor)
    sql = 'select * from instaID'
    curs.execute(sql)
    
    datas = curs.fetchall()
    print_dict = datas
    con.close()
    src_list = crawling_insta(print_dict,insta_id)
    return HttpResponse(src_list)

#스크롤을 내린다.
def scroll_down(webdriver,index):
    #webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    webdriver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    webdriver.get_screenshot_as_file('test'+str(index)+'.png')
    time.sleep(5)

#google api에 객체 분석
@csrf_exempt
def localize_objects_uri(uri, save_path, tag, index):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    image = vision.types.Image()
    image.source.image_uri = uri

    objects = client.object_localization(
        image=image).localized_object_annotations

    #print('Number of objects found: {}'.format(len(objects)))
    classify_image = ['Person', 'Man', 'Woman']

    #사람으로 분류된 사진만 저장
    for object_ in objects:
        if object_.name in classify_image: # 남자, 여자도 추가해야함
            return image.source.image_uri
            #print('\n{} (confidence: {})'.format(object_.name, object_.score))
            #urllib.request.urlretrieve(image.source.image_uri, save_path + tag + '_' +str(index)+'.jpg')
            # print('Normalized bounding polygon vertices: ')
            # for vertex in object_.bounding_poly.normalized_vertices:
            #     print(' - ({}, {})'.format(vertex.x, vertex.y))

@csrf_exempt
def crawling_insta(insta_dict,insta_id):
    # chrome 창을 띄우지 않고 크롤링
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('no-sandbox')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome('chromedriver', options=options) # 설치경로입력

    driver.implicitly_wait(10)

    tag = insta_id # id
    url = 'https://www.instagram.com/' + tag # id + instargram address
    
    for item in insta_dict:
        ID = item['id']
        PW = item['pw']
        
    # ID = insta_dict['id']
    # PW = insta_dict['pw']

    #드라이버 실행
    driver.get(url)

    # 비공개 계정은 프로필 사진을 담아내는 클래스가 다름 ('be6sR')
    try:
        picture = driver.find_element_by_class_name('_6q-tv')
    except NoSuchElementException as exception:
        print("비공개 계정이라서 접근할 수 없습니다.")
        exit()
    
    driver.get_screenshot_as_file('test.png')
    totallist = driver.find_elements_by_class_name('g47SY')
    profile = driver.find_element_by_class_name('_6q-tv')
    print("프로필 사진:", profile.get_attribute('src'))
    print("총 게시물의 갯수 :", totallist[0].text)
    print("팔로워 :", totallist[1].text)

    photo_list = []

    if totallist[0].text == '0':
        print("작성한 게시글이 없음")
        return HttpResponse(5)


    #total_count = int(totallist[0].text)

    # 크롤링 중 로그인 문제로 인한 로그인 선행
    time.sleep(1)
    driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/span/a[1]/button').click()
    driver.find_elements_by_name('username')[0].send_keys(ID)
    driver.find_elements_by_name('password')[0].send_keys(PW)
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/section/main/div/article/div/div[1]/div/form/div[4]/button').submit()
    
    index = 0

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
        
        scroll_down(driver,index)
        
        index +=1

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

    save_path = '/home/sungmin_lim/Downloads/workspace/StyleView_Server/Documents/StyleView/image/'+tag+'/'

    if not os.path.isdir(save_path):
        os.makedirs(save_path)

# for i, n in enumerate(photo_list):
#     urllib.request.urlretrieve(n['src'], save_path + tag + str(i)+'.jpg')

    index = 0
   
    src_list = []
    

    for n in tmp_list:
        src_dict = {}
        src_dict['src'] = localize_objects_uri(n, save_path, tag, index)
        src_list.append(src_dict)
        index+=1
        
    driver.quit()
    
    json_datas = json.dumps(src_list)
    
    return json_datas

@csrf_exempt
def find_insta_id(request):
    insta_id = request.POST.get('input_insta_id', '')
    UserID = request.POST.get('UserID', '')

    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'select sID from savedInstaID where sInstaID = %s and sID = %s'
        curs.execute(sql, (insta_id, UserID))

        datas = curs.fetchone()
        print_datas = datas

    finally:
        con.close()

    if print_datas == None:
        print('input instagram id is not existed')
    else:
        print('input instagram id is in db')
        return HttpResponse(1)

   #insta_id = 'hm_son7'

    options = webdriver.ChromeOptions ()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('disable-dev-shm-usage')
    options.add_argument('no-sandbox')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome('chromedriver', options = options)

    driver.implicitly_wait(10)

    url = 'https://www.instagram.com/' + insta_id

    driver.get(url)

    try:
        picture = driver.find_element_by_class_name('_6q-tv')
    except NoSuchElementException as exception:
        print('비공개 계정이라서 접근할 수 없습니다.')
        exit()
        return HttpResponse(0)


    totallist = driver.find_elements_by_class_name('g47SY')
    profile = driver.find_element_by_class_name('_6q-tv')


    insta_info_dict = {}
    insta_info_dict['ID'] = insta_id
    print(profile.get_attribute('src'))
    insta_info_dict['url'] = profile.get_attribute('src')#profile image
    insta_info_dict['followers'] = totallist[1].text #follower

    driver.quit()
    
    errornum = 0
    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'insert into savedInstaID(sInstaID, sUrl, sFollower, sID) values (%s, %s, %s, %s)'
        curs.execute(sql, (insta_id, insta_info_dict['url'], insta_info_dict['followers'], UserID))
        con.commit()

    except con.Error as error:
        con.rollback()
        print('error inserting record into mysql')
        print(error)
        errornum = 2

    finally:
        con.close()

    if errornum == 2 :
        return HttpResponse(2)


    json_datas = json.dumps(insta_info_dict)
    print(json_datas)
    return HttpResponse(json_datas)

#user login
@csrf_exempt
def add_user(request):
    input_uid = request.POST.get('UserID', '')
    input_upw = request.POST.get('UserPW', '')
    input_umail = request.POST.get('UserEMAIL', '')
    errornum = 0

    try:
        con = pymysql.connect(host = 'localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'insert into userinfo values(%s, %s, %s)'
        curs.execute(sql, (input_uid, input_upw, input_umail))
        con.commit()
        errornum =1

    except con.Error as error:
        con.rollback()
        print('error inserting record into mysql')
        print(error)
        errornum =0

    finally:
        con.close()

    if(errornum ==1):
        return HttpResponse(1)
    else:
        return HttpResponse(0)

@csrf_exempt
def check_id(request):
    inputID = request.POST.get('UserID', '')

    try:
        con = pymysql.connect(host='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'select uid from userinfo where uid = %s'
        curs.execute(sql, inputID)

        datas = curs.fetchone()
        print_datas = datas

    finally:
        con.close()

    if print_datas is None:
        print('cannot find duplicated id')
        return HttpResponse(1)
    else:
        print('already existed')
        return HttpResponse(0)

@csrf_exempt
def check_email(request):
    inputTel = request.POST.get('UserEMAIL', '')

    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'select umail from userinfo where umail = %s'
        curs.execute(sql, inputTel)

        datas = curs.fetchone()
        print_datas = datas
        print(datas)

    finally:
        con.close()

    if print_datas is None:
        print('cannot find duplicated email')
        return HttpResponse(1)
    else:
        print('already existed email')
        return HttpResponse(0)

@csrf_exempt
def find_id(request):
    userEMAIL = request.POST.get('find_id_email', '')

    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'select uid from userinfo where umail = %s'
        curs.execute(sql, userEMAIL)

        datas = curs.fetchone()
        print_datas =datas

    finally:
        con.close()

    if print_datas == None:
        print('cannot find id')
        return HttpResponse(0)
    else:
        print(print_datas[0])
        return HttpResponse(print_datas[0])

@csrf_exempt
def find_pw(request):
    userID = request.POST.get('find_pw_user_id', '')
    userEMAIL = request.POST.get('find_pw_user_email', '')
    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'select upw from userinfo where uid =%s and umail =%s'
        curs.execute(sql, (userID, userEMAIL))

        datas = curs.fetchone()
        print_datas= datas
        print(print_datas)

    finally:
        con.close()

    if print_datas == None:
        print('cannot find pw')
        return HttpResponse(0)
    else:
        return HttpResponse(print_datas[0])

@csrf_exempt
def app_login(request):
    UserID = request.POST.get('UserID', '')
    UserPW = request.POST.get('UserPW', '')
    login_success = 0 # if error occurs, return 0

    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'select uid from userinfo where uid = %s'
        curs.execute(sql, UserID)
        id_data = curs.fetchone()

        if id_data is None:
            print('this id is not in db')
            login_success = 0

        else:
            print('id is in database')
            sql = 'select upw from userinfo where uid =%s'
            curs.execute(sql, UserID)
            pw_datas = curs.fetchone()

            if pw_datas is None:
                print('pw is not same')
                login_success = 2
            elif UserPW == pw_datas[0]:
                print('id and pw are same')
                login_success = 1
            else:
                print('pw is not same')
                login_success = 2

    finally:
        con.close()

    if login_success == 1:
        print('login success!')
        return HttpResponse(1)

    else:
        print('login fail')

        if login_success == 2:
            print('pw is not same')
            return HttpResponse(2)

        else:
            print('cannot find id')
            return HttpResponse(0)

@csrf_exempt
def saved_instaID(request):
    UserID = request.POST.get('UserID', '')
    #UserID = 'hello'

    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor(pymysql.cursors.DictCursor)
        sql = 'select * from savedInstaID where sID = %s'
        curs.execute(sql, UserID)
        datas = curs.fetchall()
        json_data = json.dumps(datas)

    finally:
        con.close()

    if datas is None:
        print("This id did't have any saved instagram ID")
        return HttpResponse(0)

    elif len(datas) == 0:
        print("This id did't have any saved instagram ID")
        return HttpResponse(0)

    else:
        return HttpResponse(json_data)

@csrf_exempt
def delete_instaID(request):
    insta_id = request.POST.get('insta_id', '')
    UserID = request.POST.get('UserID', '')
    errornum = 0

    try:
        con = pymysql.connect(host ='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'delete from savedInstaID where sInstaID = %s and sID = %s'
        curs.execute(sql, (insta_id, UserID))
        
        if curs.rowcount == 1:
            errornum = 1
        con.commit()

    except con.Error as error:
        con.rollback()
        print('delete error in mysql')
        print(error)

    finally:
        con.close()

    if errornum == 1:
        print('delete success !')
        return HttpResponse(1)

    else:
        print('delete fail')
        return HttpResponse(0)

@csrf_exempt
def show_saved_Image(request):
    #insta_id = 'hello'
    login_id = request.POST.get('login_id','')
    errornum = 0

    try:
        con = pymysql.connect(host='localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor(pymysql.cursors.DictCursor)
        sql = 'select iURL from savedInstaImage where iID = %s'
        curs.execute(sql, login_id)

        datas = curs.fetchall()
        json_data = json.dumps(datas)

    finally:
        con.close()

    if datas is None:
        print("This user didn't save image in user ID")
        return HttpResponse(0)
    elif len(datas) == 0:
        print("This user didn'y save image in user ID")
        return HttpResponse(0)

    else:
        return HttpResponse(json_data)

@csrf_exempt
def save_selected_image(request):
    login_id = request.POST.get('login_id','')
    image_src = request.POST.get('image_src','')
    image_src = image_src.replace('*','&')
    print(image_src)
    errornum = 0

    try:
        con = pymysql.connect(host = 'localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'insert into savedInstaImage(iID, iURL) values (%s, %s)'
        curs.execute(sql, (login_id, image_src))
        con.commit()

    except con.Error as error:
        con.rollback()
        print('error inserting selected image in your account')
        print(error)
        errornum = 2

    finally:
        con.close()

    if errornum == 2:
        return HttpResponse(1)

    else:
        return HttpResponse(0)

@csrf_exempt
def delete_selected_image(request):
    login_id = request.POST.get('login_id', '')
    image_src = request.POST.get('image_src','')
    image_src = image_src.replace('*', '&')
    errornum = 0

    try:
        con = pymysql.connect(host = 'localhost', user=os.environ.get('MYSQL_USER'), password=os.environ.get('MYSQL_PWD'), db=os.environ.get('MYSQL_DB'), charset='utf8')
        curs = con.cursor()
        sql = 'delete from savedInstaImage where iID = %s and iURL = %s'
        curs.execute(sql, (login_id, image_src))

        if curs.rowcount == 1:
            errornum = 1
        con.commit()

    except con.Error as error:
        con.rollback()
        print('delete image error in mysql')
        print(error)

    finally:
        con.close()

    if errornum == 1:
        print('delete image complete !')
        return HttpResponse(1)

    else:
        print('delete fail')
        return HttpResponse(0)

