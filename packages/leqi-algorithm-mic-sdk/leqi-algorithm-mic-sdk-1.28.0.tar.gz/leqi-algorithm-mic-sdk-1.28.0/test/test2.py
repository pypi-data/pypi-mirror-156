import oss2
access_key_id = 'LTAIQ8Lif1HHVkXd'
access_key_secret = 'I59E6I9jPA6TpFTBqbHaauowU8lvoX'
bucket_name = 'testleqi'
endpoint = 'https://oss-cn-shanghai.aliyuncs.com'  # 外网服务器地址
data = open('1.dat', 'rb').read().decode().split('\n')