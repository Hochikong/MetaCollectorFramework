UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
      '537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')

HEADER = {
    "User-Agent": UA
}

proxies = {"http": 'socks5://127.0.0.1:5082', 'https': 'socks5h://127.0.0.1:5082'}
