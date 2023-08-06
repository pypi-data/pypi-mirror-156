# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2022-06-22 09:38:56
@LastEditTime: 2022-06-22 18:07:34
@LastEditors: HuangJianYi
@Description: 
"""
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from urllib.parse import quote_plus
from base64 import decodebytes, encodebytes
import json


class AliPayHelper:
    """
    :description: 支付宝支付帮助类
    """
    def __init__(self, appid, app_private_key, alipay_public_key, notify_url, debug=False):
        """
        :description: 初始化
        :param appid:支付宝分配给开发者的应用ID
        :param app_private_key:应用私钥
        :param alipay_public_key:阿里公钥
        :param notify_url:异步通知地址
        :param debug:True沙箱 False正式环境
        :return:
        :last_editors: HuangJianYi
        """
        self.appid = appid
        self.notify_url = notify_url
        self.app_private_key = RSA.importKey("-----BEGIN RSA PRIVATE KEY-----\n" + app_private_key + "\n-----END RSA PRIVATE KEY-----")
        self.alipay_public_key = RSA.importKey("-----BEGIN RSA PUBLIC KEY-----\n" + alipay_public_key + "\n-----END RSA PUBLIC KEY-----")

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def trade_page_pay(self, subject, out_trade_no, total_amount, return_url, **kwargs):
        """
        :description: PC场景下单
        :param subject:订单标题。注意：不可使用特殊字符，如 /，=，& 等。
        :param out_trade_no:商户订单号。由商家自定义，64个字符以内，仅支持字母、数字、下划线且需保证在商户端不重复。
        :param total_amount:订单总金额，单位为元，精确到小数点后两位，取值范围为 [0.01,100000000]。金额不能为0。
        :param return_url:同步通知地址(跳转地址)
        :return:
        :last_editors: HuangJianYi
        """
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
        }

        biz_content.update(kwargs)
        data = self.convert_request_param("alipay.trade.page.pay", biz_content, return_url)
        return self.__gateway + "?" + self.key_value_url(data)

    def convert_request_param(self, method, biz_content, return_url=None):
        """
        :description: 转换请求参数
        :param method:方法名
        :param biz_content:业务内容
        :param alipay_public_key:阿里公钥
        :param return_url:同步地址
        :return:
        :last_editors: HuangJianYi
        """
        data = {"app_id": self.appid, "method": method, "charset": "utf-8", "sign_type": "RSA2", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "version": "1.0", "biz_content": biz_content}
        if return_url is not None:
            data["return_url"] = return_url
        data["notify_url"] = self.notify_url
        return data

    def key_value_url(self, data):
        """
        :description: 拼接参数
        :param data:参数字典
        :return:
        :last_editors: HuangJianYi
        """
        data.pop("sign", None)
        unsigned_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.get_sign(unsigned_string.encode("utf-8"))
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def get_sign(self, data):
        """
        :description: 生成签名
        :param unsigned_string:参数拼接字符串
        :return:
        :last_editors: HuangJianYi
        """
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(data))
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def check_sign(self, data, signature):
        """
        :description: 校验签名
        :param data:参数字典
        :param signature:签名值
        :return:
        :last_editors: HuangJianYi
        """
        if "sign_type" in data:
            data.pop("sign_type")
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        signer = PKCS1_v1_5.new(self.alipay_public_key)
        digest = SHA256.new()
        digest.update(message.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False
