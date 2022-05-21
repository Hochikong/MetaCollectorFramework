import os
import time
from typing import List

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def iter_downloader(web_elements: List[WebElement],
                    download_path: str,
                    anchor_text: str,
                    file_name_handler: callable = None,
                    **kwargs) -> str:
    """
    执行文件下载并返回文件的绝对路径--遍历版本

    :param web_elements:
    :param download_path:
    :param anchor_text:
    :param file_name_handler:
    :param kwargs:
    :return:
    """
    down_dir = download_path
    if not download_path.endswith(os.sep):
        down_dir = download_path + os.sep

    before_download = list(filter(lambda file: file.endswith('csv'), os.listdir(download_path)))
    time.sleep(2)

    # 点击下载
    for ele in web_elements:
        if anchor_text in ele.text:
            ele.click()
            break

    max_wait_loop = 50
    while max_wait_loop > 0:
        max_wait_loop -= 1

        after_download = list(filter(lambda file: file.endswith('csv'), os.listdir(download_path)))
        delta = list(set(after_download) - set(before_download))
        if len(delta) > 1:
            raise FileNotFoundError("可能有多个文件同时被下载到此目录，无法推断哪个才是真的文件")
        if len(delta) == 1:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    real_name = delta[0].encode('latin-1').decode('gbk')
                    os.rename(down_dir + delta[0], down_dir + real_name)
                    final_name = down_dir + real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception:
                    final_name = down_dir + delta[0]
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + delta[0]
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name
        if len(delta) == 0:
            time.sleep(2)
            continue

    raise RuntimeError("无文件下载")


def downloader(driver: Chrome,
               download_path: str,
               download_class: str = None,
               multiple_class_index: int = 0,
               file_name_handler: callable = None,
               **kwargs) -> str:
    """
    执行文件下载并返回文件的绝对路径

    :param driver: chrome driver实例
    :param download_path: 下载目录
    :param download_class: ’下载‘的class属性，用来寻找
    :param multiple_class_index: 当download_class存在多个的时候，指定选择哪个
    :param file_name_handler: 文件名处理器，为接受一个文件名和多个参数的函数
    :param kwargs: 文件名处理器参数
    :return:
    """
    down_dir = download_path
    if not download_path.endswith(os.sep):
        down_dir = download_path + os.sep

    before_download = list(filter(lambda file: file.endswith('xls'), os.listdir(download_path)))
    time.sleep(2)
    # 点击下载
    if download_class:
        driver.find_elements(By.CLASS_NAME, download_class)[multiple_class_index].click()
    else:
        driver.find_element(By.CLASS_NAME, 'download-text').click()

    max_wait_loop = 50
    while max_wait_loop > 0:
        after_download = list(filter(lambda file: file.endswith('xls'), os.listdir(download_path)))
        delta = list(set(after_download) - set(before_download))
        if len(delta) > 1:
            raise FileNotFoundError("可能有多个文件同时被下载到此目录，无法推断哪个才是真的文件")
        if len(delta) == 1:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    print("hit1")
                    real_name = delta[0].encode('latin-1').decode('gbk')
                    os.rename(down_dir + delta[0], down_dir + real_name)
                    final_name = down_dir + real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception as e:
                    print(e)
                    print("hit2")
                    final_name = down_dir + delta[0]
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + delta[0]
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name
        if len(delta) == 0:
            time.sleep(2)
            max_wait_loop -= 1
            continue


def downloaderV2022(driver: Chrome,
                    download_path: str,
                    download_class: str = None,
                    multiple_class_index: int = 0,
                    file_name_handler: callable = None,
                    primary_postfix: str = 'xls',
                    secondary_postfix: str = None,
                    **kwargs) -> str:
    """
    执行文件下载并返回文件的绝对路径

    :param driver: chrome driver实例
    :param download_path: 下载目录
    :param download_class: ’下载‘的class属性，用来寻找
    :param multiple_class_index: 当download_class存在多个的时候，指定选择哪个
    :param file_name_handler: 文件名处理器，为接受一个文件名和多个参数的函数
    :param secondary_postfix: 主文件后缀
    :param primary_postfix: 次文件后缀，如果检测到下载的文件带次文件后缀，则重命名为主后缀
    :param kwargs: 文件名处理器参数
    :return:
    """
    down_dir = download_path
    if not download_path.endswith(os.sep):
        down_dir = download_path + os.sep

    if secondary_postfix:
        before_download = list(
            filter(lambda file: file.endswith('xls') or file.endswith(secondary_postfix), os.listdir(download_path)))
    else:
        before_download = list(filter(lambda file: file.endswith('xls'), os.listdir(download_path)))

    time.sleep(2)
    # 点击下载
    if download_class:
        driver.find_elements(By.CLASS_NAME, download_class)[multiple_class_index].click()
    else:
        driver.find_element(By.CLASS_NAME, 'download-text').click()
    time.sleep(4)

    max_wait_loop = 50
    while max_wait_loop > 0:
        try:
            if secondary_postfix:
                after_download = list(filter(lambda file: file.endswith('xls') or file.endswith(secondary_postfix),
                                             os.listdir(download_path)))
            else:
                after_download = list(filter(lambda file: file.endswith('xls'), os.listdir(download_path)))

            delta = list(set(after_download) - set(before_download))
            tn = delta[0]
        except IndexError:
            max_wait_loop -= 1
            time.sleep(2)
            continue

        if len(delta) > 1:
            raise FileNotFoundError("可能有多个文件同时被下载到此目录，无法推断哪个才是真的文件")
        if len(delta) == 1:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    print("hit1")
                    real_name = tn.encode('latin-1').decode('gbk')

                    if real_name.endswith(secondary_postfix):
                        t_real_name = real_name.replace(secondary_postfix, primary_postfix)
                    else:
                        t_real_name = real_name

                    os.rename(down_dir + tn, down_dir + t_real_name)
                    final_name = down_dir + t_real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception as e:
                    print(e)
                    print("hit2")

                    if tn.endswith(secondary_postfix):
                        t_tn = tn.replace(secondary_postfix, primary_postfix)
                    else:
                        t_tn = tn

                    final_name = down_dir + t_tn
                    os.rename(down_dir + tn, down_dir + t_tn)

                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + tn
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name
        if len(delta) == 0:
            time.sleep(2)
            max_wait_loop -= 1
            continue


def custom_downloader(driver: Chrome,
                      download_path: str,
                      download_class: str = None,
                      multiple_class_index: int = 0,
                      file_name_handler: callable = None,
                      postfix: str = 'xls',
                      **kwargs) -> str:
    """
    执行文件下载并返回文件的绝对路径，支持选择不同的文件后缀

    :param driver: chrome driver实例
    :param download_path: 下载目录
    :param download_class: ’下载‘的class属性，用来寻找
    :param multiple_class_index: 当download_class存在多个的时候，指定选择哪个
    :param file_name_handler: 文件名处理器，为接受一个文件名和多个参数的函数
    :param postfix: 监测的文件后缀
    :param kwargs: 文件名处理器参数
    :return:
    """
    down_dir = download_path
    if not download_path.endswith(os.sep):
        down_dir = download_path + os.sep

    before_download = list(filter(lambda file: file.endswith(postfix), os.listdir(download_path)))
    time.sleep(2)
    # 点击下载
    if download_class:
        driver.find_elements(By.CLASS_NAME, download_class)[multiple_class_index].click()
    else:
        driver.find_element(By.CLASS_NAME, 'download-text').click()

    max_wait_loop = 50
    while max_wait_loop > 0:
        after_download = list(filter(lambda file: file.endswith(postfix), os.listdir(download_path)))
        delta = list(set(after_download) - set(before_download))
        if len(delta) > 1:
            raise FileNotFoundError("可能有多个文件同时被下载到此目录，无法推断哪个才是真的文件")
        if len(delta) == 1:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    real_name = delta[0].encode('latin-1').decode('gbk')
                    os.rename(down_dir + delta[0], down_dir + real_name)
                    final_name = down_dir + real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception as e:
                    print(e)
                    final_name = down_dir + delta[0]
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + delta[0]
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name
        if len(delta) == 0:
            time.sleep(2)
            max_wait_loop -= 1
            continue


def custom_iter_downloader(web_elements: List[WebElement],
                           download_path: str,
                           anchor_text: str,
                           file_name_handler: callable = None,
                           postfix: str = 'xls',
                           max_wait_loop: int = 50,
                           **kwargs) -> str:
    """
    执行文件下载并返回文件的绝对路径--遍历版本，支持选择文件后缀

    :param web_elements:
    :param download_path:
    :param anchor_text:
    :param file_name_handler:
    :param max_wait_loop: 最大等待循环数
    :param postfix:
    :param kwargs:
    :return:
    """
    down_dir = download_path
    if not download_path.endswith(os.sep):
        down_dir = download_path + os.sep

    before_download = list(filter(lambda file: file.endswith(postfix), os.listdir(download_path)))
    time.sleep(2)

    # 点击下载
    for ele in web_elements:
        if anchor_text in ele.text:
            ele.click()
            break

    while max_wait_loop > 0:
        max_wait_loop -= 1

        after_download = list(filter(lambda file: file.endswith(postfix), os.listdir(download_path)))
        delta = list(set(after_download) - set(before_download))
        if len(delta) > 1:
            raise FileNotFoundError("可能有多个文件同时被下载到此目录，无法推断哪个才是真的文件")
        if len(delta) == 1:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    real_name = delta[0].encode('latin-1').decode('gbk')
                    os.rename(down_dir + delta[0], down_dir + real_name)
                    final_name = down_dir + real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception:
                    final_name = down_dir + delta[0]
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + delta[0]
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name
        if len(delta) == 0:
            time.sleep(2)
            continue

    raise RuntimeError("无文件下载")


def custom_iter_downloaderV2(web_elements: List[WebElement],
                             download_path: str,
                             anchor_text: str,
                             file_name_handler: callable = None,
                             postfix: str = 'xls',
                             secondary_postfix: str = 'zip',
                             max_wait_loop: int = 50,
                             **kwargs) -> str:
    """
    执行文件下载并返回文件的绝对路径--遍历版本，支持选择备用文件后缀

    :param web_elements:
    :param download_path:
    :param anchor_text:
    :param file_name_handler:
    :param max_wait_loop: 最大等待循环数
    :param postfix: 文件后缀，
    :param secondary_postfix: 次级文件后缀，作为备用后缀方案检查文件是否下载了但是是其他类型
    :param kwargs:
    :return:
    """
    down_dir = download_path
    if not download_path.endswith(os.sep):
        down_dir = download_path + os.sep

    before_download = list(filter(lambda file: file.endswith(postfix), os.listdir(download_path)))
    before_download_sec = list(filter(lambda file: file.endswith(secondary_postfix), os.listdir(download_path)))
    time.sleep(2)

    # 点击下载
    for ele in web_elements:
        if anchor_text in ele.text:
            ele.click()
            break

    while max_wait_loop > 0:
        max_wait_loop -= 1

        after_download = list(filter(lambda file: file.endswith(postfix), os.listdir(download_path)))
        after_download_sec = list(filter(lambda file: file.endswith(secondary_postfix), os.listdir(download_path)))

        delta = list(set(after_download) - set(before_download))
        delta_sec = list(set(after_download_sec) - set(before_download_sec))

        if len(delta) > 1 or len(delta_sec) > 1:
            raise FileNotFoundError("可能有多个文件同时被下载到此目录，无法推断哪个才是真的文件")
        if len(delta) == 1 and len(delta_sec) == 0:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    real_name = delta[0].encode('latin-1').decode('gbk')
                    os.rename(down_dir + delta[0], down_dir + real_name)
                    final_name = down_dir + real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception:
                    final_name = down_dir + delta[0]
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + delta[0]
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name

        if len(delta) == 0 and len(delta_sec) == 1:
            if os.name == 'posix':
                try:
                    # linux下乱码
                    real_name = delta_sec[0].encode('latin-1').decode('gbk')
                    os.rename(down_dir + delta_sec[0], down_dir + real_name)
                    final_name = down_dir + real_name
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
                except Exception:
                    final_name = down_dir + delta_sec[0]
                    if file_name_handler:
                        return down_dir + file_name_handler(final_name, **kwargs)
                    return final_name
            else:
                final_name = down_dir + delta_sec[0]
                if file_name_handler:
                    return down_dir + file_name_handler(final_name, **kwargs)
                return final_name

        if len(delta) == 0 and len(delta_sec) == 0:
            time.sleep(2)
            continue

    raise RuntimeError("无文件下载")


def keyword_assistant_handler(abs_file_name: str, addi_desc: str) -> str:
    """
    生意参谋的'流量-选词助手-本店引流词'下载文件名处理器，为文件添加词类备注，避免文件名重复，实际上还可以用于其他模块的下载文件重命名

    :param abs_file_name: 文件名，绝对路径
    :param addi_desc: 备注，如：搜索词、长尾词
    :return: 返回文件名，不含路径
    """
    segments = abs_file_name.split(os.sep)
    pure_name = segments[-1]
    abs_prefix = os.sep.join(segments[:-1]) + os.sep

    segments_ = pure_name.split(".")
    file_type_suffix = segments_[-1]
    name_without_suffix = segments_[0]
    target_pure_name = "{}_{}.{}".format(name_without_suffix, addi_desc, file_type_suffix)
    os.rename(abs_file_name, abs_prefix + target_pure_name)
    return target_pure_name
