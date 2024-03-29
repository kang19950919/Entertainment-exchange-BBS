import logging

from qiniu import Auth, put_data

# 需要填写你的 Access Key 和 Secret Key
access_key = 'xS3gQwGczLemSOjtN35dnMuTL0SajDKJbLvEhLdt'

secret_key = 'j1LVlgAGTEXCvsTywmsRkTAp1Jnko-56566HWoDF'

# 要上传的空间
bucket_name = 'avatar'


def storage(data):
    """七牛云存储上传文件接口"""
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        # 上传文件  第二个参数是图片的名字， 如果为NOne 七牛会自动生成随机的文件名
        ret, info = put_data(token, None, data)
    except Exception as e:
        logging.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

    # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:
        storage(f.read())