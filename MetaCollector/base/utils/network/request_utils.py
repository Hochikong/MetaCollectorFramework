from selenium.webdriver import Chrome


def collect_cookie(driver: Chrome) -> str:
    raw_cookies = driver.get_cookies()
    seq = []
    for ind, ele in enumerate(raw_cookies):
        if (ind + 1) == len(raw_cookies):
            seq.append("{}={}".format(ele['name'], ele['value']))
        else:
            seq.append("{}={}; ".format(ele['name'], ele['value']))
    cookie = ''.join(seq)
    return cookie
