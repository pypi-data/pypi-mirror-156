# bloggart

#### 介绍
极速构建博客，内嵌server/database，适合全栈

#### 软件架构
软件架构说明


#### 安装教程

1.  pip3 install -i https://mirrors.aliyun.com/pypi/simple/ tornado
2.  xxxx
3.  xxxx

#### 使用说明

1.  直接使用`bloggart`命令
2.  xxxx
3.  xxxx

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

# 直接用

# 间接用

二次开发

# 注意

安全性完全没有

## 发布

```bash
python3 -m venv bloggart-venv/
source bloggart-venv/bin/activate.fish

# 调试好之后
python3 -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ setuptools wheel
python3 setup.py sdist bdist_wheel

pip3 freeze > requirements.txt
# requirements添加一个peppercorn
echo 'peppercorn' >> requirements.txt
pip3 download -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ -d dist/

cd dist/
dir2pi -S .
scp -r simple/ root@39.97.232.223:/root/pypi/
pip3 install -i http://www.hohohaha.cn:8000/simple/ bloggart==0.0.2 --trusted-host www.hohohaha.cn
```

## 上传到pypi

```bash
python3 -m venv bloggart-venv/
source bloggart-venv/bin/activate.fish
rm -rf dist/*
python3 setup.py sdist bdist_wheel
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ twine
python3 -m twine upload dist/*
```

## 安装

```bash
pip3 install -i https://pypi.python.org/simple bloggart==0.0.9
```

## 开发时

使用开发虚拟环境
```bash
python3 -m venv bloggart-dev-venv/
source bloggart-dev-venv/bin/activate.fish
```

在src目录下工作，如:
```bash
cd src

pwd
/home/xiabo/gitee-xiabo0816/bloggart/src

python3 bloggart/header.py -c bloggart/config.ini -p 8888
```

# repeater示例


配置文件内容
```ini
; tcp本机中继

[REPEATER]
local_uri=http://127.0.0.1:8000/concate
proxy_uri=repeater
```


```bash
# 原本服务的请求是
curl -X POST 127.0.0.1:8000/concate -d '{ "TPL_TYPE" : "转移支付提前下达", "PRO_START_YEAR" : "2018", "PRO_NAME" : "省财政“三农”转移支付资金", "FISCAL_YEAR" : "2018", "CREATE_TIME" : "2018年6月30日", "EXP_FUNC_CODE" : "农林水支出—农业—其他农业支出（2130199）", "GOV_BGT_ECO_CODE" : "51301-上下级政府间转移性支出", "FOUND_TYPE_CODE" : "一般公共预算", "TP_FUNC_CODE" : "农林水支出—农业—其他农业支出（2130199）", "PRO_PAY_DIC_CODE" : "支出", "POLICY_NAME" : "《财政部关于开展田园综合体建设试点工作的通知》（财办〔2017〕29号）和《关于做好2017年田园综合体试点工作的意见》（财办农〔2017〕71号）", "INCOME_SORT_CODE" : "1100224农村综合改革转移支付收入", "TEMPLATE_ID": "1" }'

# repeater转发后的是
# 注意结尾有-L参数
curl -X POST 127.0.0.1:8888/blogging/repeater -d '{ "TPL_TYPE" : "转移支付提前下达", "PRO_START_YEAR" : "2018", "PRO_NAME" : "省财政“三农”转移支付资金", "FISCAL_YEAR" : "2018", "CREATE_TIME" : "2018年6月30日", "EXP_FUNC_CODE" : "农林水支出—农业—其他农业支出（2130199）", "GOV_BGT_ECO_CODE" : "51301-上下级政府间转移性支出", "FOUND_TYPE_CODE" : "一般公共预算", "TP_FUNC_CODE" : "农林水支出—农业—其他农业支出（2130199）", "PRO_PAY_DIC_CODE" : "支出", "POLICY_NAME" : "《财政部关于开展田园综合体建设试点工作的通知》（财办〔2017〕29号）和《关于做好2017年田园综合体试点工作的意见》（财办农〔2017〕71号）", "INCOME_SORT_CODE" : "1100224农村综合改革转移支付收入", "TEMPLATE_ID": "1" }' -L
```