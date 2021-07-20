# django-weapp

基于`Django3`和`Django-Rest-Framework`的社交系统

响应分类

1. 信息响应(100–199)
2. 成功响应(200–299)
3. 重定向(300–399)
4. 客户端错误(400–499)
5. 服务器错误 (500–599)

Redis Key 命名规范

`oauth:users:uid:1234:username`

`oauth:users:uid:1234:nickname`

`oauth:gettoken:email:123456@qq.com:captcha`

`oauth:setpasswd:phone:123456:captcha`

`oauth:setemail:email:123456@qq.com:captcha`

`oauth:setphone:phone:123456:captcha`
