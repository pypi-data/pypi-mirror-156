def scroll(scroll_num):
    count = 0
    scroll_num = int(scroll_num)
    while count<scroll_num:
        web.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        print('scrolled',(count+1),'time')
        time.sleep(3)
        count += 1

def scroll_little_bit(scroll_num):
    count = 0
    scroll_num = int(scroll_num)
    while count<scroll_num:
        web.execute_script('window.scrollBy(0,250)')
        print('scrolled',(count+1),'time')
        time.sleep(3)
        count += 1

def login_mobile():
    url = 'https://m.weibo.cn/'
    web = Chrome()
    web.get(url)
    time.sleep(5)
    confirm  = input('login complete[y/n]:')

    if confirm == 'y':
        print('Congratulations! Now you can proceed')
    else:
        print('Please quit browser and try again. Log in process can take a while, please wait in patient if stucked.')

def login_web():
    url = 'https://weibo.com/newlogin?tabtype=weibo&gid=102803&openLoginLayer=0&url=https%3A%2F%2Fweibo.com%2F'
    web = Chrome()
    web.get(url)
    time.sleep(10)
    web.find_element_by_xpath('//*[@id="__sidebar"]/div/div[1]/div[1]/div/button').click()
    confirm  = input('login complete[y/n]:')

    if confirm == 'y':
        print('Congratulations! Now you can proceed')
    else:
        print('Please quit browser and try again. Log in process can take a while, please wait in patient if stucked.')


def hot_people(hashtag):
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[1]').click()
    hashtag = str(hashtag)
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(hashtag)
    confirm = input('confirm[y/n]:')
    if confirm == 'y':
        print('Proceed')
    else:
        a = str('Process stopped. Clear search bar ,refresh webpage and Try again')
        return a
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(
        Keys.ENTER)
    web.switch_to.window(web.window_handles[-1])

    time.sleep(3)

    intro_list = []
    name_list = []
    hot_div_list = web.find_elements_by_xpath('//*[@id="pl_right_side"]/div[2]/div/div[2]/ul/li')
    for i in range(len(hot_div_list)):
        hot_div_list = web.find_elements_by_xpath('//*[@id="pl_right_side"]/div[2]/div/div[2]/ul/li')
        hot_div_list[i].find_element_by_xpath('./span[@class="avator"]/a/i[@class="hoverMask"]').click()
        intro = None
        name = None
        time.sleep(3)
        try:
            name = web.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[2]/div[2]/main/div/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div')
        except:
            print("error!")
            name_list.append('None')
        if name != None:
            name = name.text
            print(name)
            name_list.append(name)
        try:
            intro = web.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[2]/div[2]/main/div/div/div[2]/div[1]/div[1]/div[3]/div/div/div[1]/div[2]/div/div/div[2]')
        except:
            print("error!")
            intro_list.append('None')
        if intro != None:
            intro = intro.text
            print(intro)
            intro_list.append(intro)
        time.sleep(2)
        web.back()
        print('back')
    dic = {'Name:': name_list, 'Intro': intro_list}
    df = pd.DataFrame(dic)
    return df

def search_mobile(user_name):
    user_name = str(user_name)
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[1]/a/aside/label/div').click()
    time.sleep(3)
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[1]/div/div/div[2]/form/input').send_keys(user_name)
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[1]/div/div/div[2]/form/input').send_keys(Keys.ENTER)
    time.sleep(2)
    web.switch_to.window(web.window_handles[-1])
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[3]/div/div/div[1]/div').click()

def repo_passive_name(scroll_num):
    name_list = []
    web.switch_to.window(web.window_handles[-1])
    try:
        web.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[4]/div[1]/div[1]').click()
        print('clicked')
    except:
        scroll_little_bit(2)
        time.sleep(2)
        web.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[4]/div[1]/div[1]').click()
        print('clicked')
    time.sleep(3)
    scroll_num = int(scroll_num)
    scroll(scroll_num)
    time.sleep(3)
    div_list = web.find_elements_by_xpath('//*[@id="app"]/div[1]/div/div[4]/div[2]/div')
    for div in div_list:
        try:
            name = div.find_element_by_xpath('./div/div/div/div/div/div[1]/div/div/h4').text
        except:
            print("error!")
        if name != None:
            name_list.append(name)
    print(len(name_list))
    return (name_list)


def repo_name_initiative(scroll_num):
    web.switch_to.window(web.window_handles[-1])
    scroll_num = int(scroll_num)
    scroll(scroll_num)
    time.sleep(3)

    repo_name_list = []
    div_list = web.find_elements_by_xpath('//*[@id="app"]/div[1]/div[1]/div')
    for div in div_list[3:]:
        try:
            repo_name = div.find_element_by_xpath('./div/div/div/article/div[3]/div[1]/span[1]/a').text
            print('repo get')
        except:
            repo_name = None
            repo_name_list.append(None)
        if repo_name != None:
            repo_name_list.append(repo_name)
    return repo_name_list

def make_list_num_df(list_long):
    list_long = np.array(list_long)
    unique_list = np.unique(list_long)
    unique_list = list(unique_list)
    dic = {unique_list[0]:0}
    for i in range(len(unique_list)):
        dic_new = {unique_list[i]:0}
        dic.update(dic_new)
    for name in list_long:
        if name in unique_list:
            dic[name] = dic[name]+1
    name_list = list(dic.keys())
    value_list = list(dic.values())
    Dic = {'Name':name_list,'Num':value_list}
    df = pd.DataFrame(Dic)
    return df

def clean_repo_name(repo_name_list):
    new_list = []
    for name in repo_name_list:
        if name != None:
            new_list.append(name)
    return new_list


def get_content_and_time(scroll_num):
    content_list = []
    time_list = []
    web.switch_to.window(web.window_handles[-1])
    scroll_num = int(scroll_num)
    scroll(scroll_num)
    time.sleep(3)
    div_list = web.find_elements_by_xpath('//*[@id="app"]/div[1]/div[1]/div')
    for div in div_list:
        try:
            content = div.find_element_by_xpath('./div/div/div/article/div[2]/div[1]').text
            print('-----', content, '-----')
        except:
            print('error!')
            content = None
        if content != None:
            content_list.append(content)
        try:
            time_var = div.find_element_by_xpath('./div/div/div/header/div/div/h4/span[1]').text
            print('-----', time_var, '-----')
        except:
            print('error!')
            time_var = None
        if time_var != None:
            time_list.append(time_var)
    dic = {"Content": content_list, 'Time': time_list}
    df = pd.DataFrame(dic)

    return df

def find_repo_in_content(content_list):
    repo_name_2 = []
    repostRegex = re.compile(r'@[\u4e00-\u9fa5]+:')
    for con in content_list:
        name = repostRegex.search(con)
        if name != None:
            name = name.group()
            repo_name_2.append(name)
    return repo_name_2

def fan_num_mobile(user_name):
    search_mobile(user_name)
    time.sleep(3)
    fan_num = web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[1]/div/div[4]/div[2]/div[2]/span').text
    return fan_num


def fan_num_web(user_name):
    user_name = str(user_name)
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[1]').click()
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(
        user_name)
    confirm = input('confirm[y/n]:')

    if confirm == 'y':
        print('Proceed')
    else:
        a = str('Process stopped. Clear search bar ,refresh webpage and Try again')
        return a
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(
        Keys.ENTER)
    web.switch_to.window(web.window_handles[-1])
    time.sleep(3)
    fan_num = web.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[2]/div[1]/div/div[2]/p/span').text
    return fan_num[3:]


def get_repo_like_ratio(user_name, scroll_num):
    search_mobile(user_name)
    time.sleep(3)

    web.switch_to.window(web.window_handles[-1])
    scroll_num = int(scroll_num)
    scroll(scroll_num)
    time.sleep(3)

    ratio_list = []
    div_list = web.find_elements_by_xpath('//*[@id="app"]/div[1]/div[1]/div')
    for div in div_list:
        try:
            like = div.find_element_by_xpath('./div/div/div/footer/div[3]/h4').text
        except:
            print('error!')
            like = None
        if like == '赞':
            like = int(0)
        if like != None and '万' in str(like):
            like = like[:-1]
            like = float(like) * 10000

        try:
            repo = div.find_element_by_xpath('./div/div/div/footer/div[1]/h4').text
        except:
            print('error!')
            repo = None
        if repo == '转发':
            repo = 0
        if repo != None and '万' in str(repo):
            repo = repo[:-1]
            repo = float(repo) * 10000

        if like != None and repo != None and like != 0:
            r_ratio = int(repo) / int(like)
            ratio_list.append(r_ratio)

        else:
            ratio_list.append(int(0))

    ave_ratio = sum(ratio_list) / len(ratio_list)
    print(ave_ratio)

    return ave_ratio


def search_topic_general(hashtag, page_num):
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[1]').click()
    hashtag = str(hashtag)
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(hashtag)
    confirm = input('confirm[y/n]:')
    if confirm == 'y':
        print('Proceed')
    else:
        a = str('Process stopped. Clear search bar ,refresh webpage and Try again')
        return a
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(
        Keys.ENTER)
    web.switch_to.window(web.window_handles[-1])

    time.sleep(3)
    web.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a').click()
    time.sleep(3)

    user_name_list = []
    weibo_content_list = []
    weibo_time_list = []
    likes_list = []

    page_num = int(page_num)
    for i in range(page_num):
        print('page', i + 2, 'loading')
        div_list = web.find_elements_by_xpath('//*[@id="pl_feedlist_index"]/div[4]/div')
        for div in div_list:
            user_name = div.find_element_by_xpath(
                './div[@class="card"]/div[@class="card-feed"]/div[@class="content"]/div[@class="info"]/div[2]/a').text
            content = div.find_element_by_xpath(
                './div[@class="card"]/div[@class="card-feed"]/div[@class="content"]/p[@class="txt"]').text
            weibo_time = div.find_element_by_xpath(
                './div[@class="card"]/div[@class="card-feed"]/div[@class="content"]/p[@class="from"]/a').text
            likes = div.find_element_by_xpath('./div[@class="card"]/div[@class="card-act"]/ul/li[3]').text

            user_name_list.append(user_name)
            weibo_content_list.append(content)
            weibo_time_list.append(weibo_time)
            likes_list.append(likes)

        print('page', i + 2, 'complete')
        print('Turning pages, might take a few second. Chekck your connection if stucked.')
        print('-----------------')

        if 0 <= i < (page_num - 2):
            web.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a[2]').click()
        else:
            break

    print('got', len(user_name_list), 'items in total')

    colum_list = ['User Name', 'Content', 'Post Time', 'Likes']
    dic = {colum_list[0]: user_name_list, colum_list[1]: weibo_content_list, colum_list[2]: weibo_time_list,
           colum_list[3]: likes_list}
    df = pd.DataFrame(dic)
    return df


def search_keyword_general(hashtag, page_num):
    web.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[1]').click()
    hashtag = str(hashtag)
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(hashtag)
    confirm = input('confirm[y/n]:')
    if confirm == 'y':
        print('Proceed')
    else:
        a = str('Process stopped. Clear search bar ,refresh webpage and Try again')
        return a
    web.find_element_by_xpath(
        '//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[1]/div/div[2]/div/span/form/div/input').send_keys(
        Keys.ENTER)
    web.switch_to.window(web.window_handles[-1])

    time.sleep(3)

    user_name_list = []
    weibo_content_list = []
    weibo_time_list = []
    likes_list = []

    page_num = int(page_num)
    for i in range(page_num):
        print('page', i + 1, 'loading')
        div_list = web.find_elements_by_xpath('//*[@id="pl_feedlist_index"]/div[2]/div')
        for div in div_list[1:]:
            try:
                user_name = div.find_element_by_xpath(
                    './div[@class="card"]/div[@class="card-feed"]/div[@class="content"]/div[@class="info"]/div[2]/a').text
            except:
                print("error!")
                user_name_list.append('None')

            if user_name != None:
                user_name = str(user_name)
                user_name_list.append(user_name)
            try:
                content = div.find_element_by_xpath(
                    './div[@class="card"]/div[@class="card-feed"]/div[@class="content"]/p[@class="txt"]').text
            except:
                print("error!")
                weibo_content_list.append('None')
            if content != None:
                content = str(content)
                weibo_content_list.append(content)
            try:
                weibo_time = div.find_element_by_xpath(
                    './div[@class="card"]/div[@class="card-feed"]/div[@class="content"]/p[@class="from"]/a[1]').text
            except:
                print("error!")
                weibo_time_list.append('None')
            if weibo_time != None:
                weibo_time = str(weibo_time)
                weibo_time_list.append(weibo_time)
            try:
                likes = div.find_element_by_xpath('./div[@class="card"]/div[@class="card-act"]/ul/li[3]/a').text
            except:
                print("error!")
                likes_list.append('None')
            if likes != None:
                likes = str(likes)
                likes_list.append(likes)

        print('page', i + 1, 'complete')
        print('Turning pages, might take a few second. Chekck your connection if stucked.')
        print('-----------------')

        if i == 0:
            web.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[3]/div/a').click()
        elif 0 < i < (page_num - 1):
            web.find_element_by_xpath('//*[@id="pl_feedlist_index"]/div[3]/div/a[2]').click()
        else:
            break

    print('got', len(user_name_list), 'items in total')

    colum_list = ['User Name', 'Content', 'Post Time', 'Likes']
    dic = {colum_list[0]: user_name_list, colum_list[1]: weibo_content_list, colum_list[2]: weibo_time_list,
           colum_list[3]: likes_list}
    df = pd.DataFrame(dic)
    return df