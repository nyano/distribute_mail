# distribute_mail
多附件、多收件人的相同邮件分发  

自动发送邮件装置  
1.首先请确认当前文件夹有config.ini  
[server]  
    smtp_server =       # SMTP服务器  
    smtp_port =         # SMTP端口  
    smtp_ssl =          # True False 使用SSL加密  
    smtp_user =         # 发件人账号  
    smtp_password =     # 发件人密码  
[sender]  
    sender_name =        # 发件人名称  
    sender_address =     # 发件人地址  
[body]  
    subject =           # 邮件主题  
    content =           # 邮件内容  

2.然后创建子文件夹，子文件夹中包含config.ini文件，才会识别该文件夹，内容如下。to_1、to_2为第一个收件人、第二个收件人，以此类推。 一个子目录为多个收件人但发送相同的附件，如果要不同的附件则创建不同的子目录。
把附件直接放在该文件夹内即可。  
[to_1]  
    receiver_name =     # 收件人名称  
    receiver_address =  # 收件人地址  
[to_2]  
    receiver_name =     # 收件人名称  
    receiver_address =  # 收件人地址  
3.如果某个目录不想发了，则创建一个not子目录，直接把子文件夹拖进去即可，不会识别not子目录。    
4.直接运行程序会显示当前有效的设置，以及有效的子文件夹内容。确认下发送的信息是否正确，不要发错！！！    
5.如果要发送邮件，则后面加上-sender参数即可。帮助信息为-help参数。  
6.发送后，保存发送结果到log.log文件中。如有错误，请阅读log.log。  
7.注意！！！config.ini中的发件人邮箱密码没有做加密，我想想是自用的，所以没做加密，请不要使用后传播config.ini！！！ 
8.所有邮件的邮件主题和内容相同，仅收件人和附件不一样。

PS.我本来想写邮件内容中添加变量的，想想算了，直接把想区分的直接写个文件放附件里不就行了？
