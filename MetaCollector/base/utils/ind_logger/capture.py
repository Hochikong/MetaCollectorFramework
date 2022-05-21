import pyscreenshot as piccap


def capture_full_screenshot(filename: str) -> bool:
    """把全屏截图导出到指定路径的指定文件中

    :param filename: 文件名，可以包含路径信息
    :return: 成功的话返回True否则False
    """
    try:
        im = piccap.grab()
        im.save(filename)
        return True
    except Exception as e:
        print(e)
        return False
