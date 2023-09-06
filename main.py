
import argparse
import configparser
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from loguru import logger

# 读取config.ini文件
def read_config():
    config = configparser.ConfigParser()
    if not os.path.exists('./config.ini'):
        raise FileNotFoundError("配置文件config.ini不存在")
    config.read('./config.ini')
    return config

# 获取文件夹中的config.ini内容和文件列表
def get_folder_info(folder):
    config_file = os.path.join(folder, 'config.ini')
    if not os.path.exists(config_file):
        return None, None
    config = configparser.ConfigParser()
    config.read(config_file)
    files = [file for file in os.listdir(folder) if file != 'config.ini']
    return config, files

# 发送邮件
def send_email(server, sender, receiver, subject, content, files):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'plain'))

    for file in files:
        file_name = os.path.basename(file)  # 获取文件名
        with open(file, 'rb') as attachment:
            part = MIMEApplication(attachment.read())
        part.add_header('Content-Disposition', 'attachment', filename=file_name)
        msg.attach(part)

    if server['smtp_ssl'].lower() == 'true':
        smtp_server = smtplib.SMTP_SSL(server['smtp_server'], int(server['smtp_port']))
    else:
        smtp_server = smtplib.SMTP(server['smtp_server'], int(server['smtp_port']))

    smtp_server.login(server['smtp_user'], server['smtp_password'])
    smtp_server.sendmail(sender, receiver, msg.as_string())
    smtp_server.quit()

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-help', action='store_true', help='帮助')
    parser.add_argument('-sender', action='store_true', help='发送有config.ini的子文件邮件')
    return parser.parse_args()

# 主函数
def main():
    args = parse_arguments()
    
    if args.help:
        print("""
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
""")
        exit(0)

    if not args.sender:
        print('先来确认一下信息\n')
        config = read_config()
        # 输出config.ini中的变量
        for section in config.sections():
            print(f'[{section}]')
            for option in config.options(section):
                print(f'{option} = {config.get(section, option)}')

        print('----\n')
        print('以下为即将发送的邮件')

    folder_ok = []
    folder_no = []

    # 遍历所有子文件夹
    for folder in os.listdir('.'):
        if folder != 'not' and os.path.isdir(folder):
            folder_path = os.path.abspath(folder)
            # folder_path = os.path.join(folder_path, '')
            config, files = get_folder_info(folder)
            if config is None or files is None:
                folder_no.append(folder)
            else:
                recipients = []
                for section in config.sections():
                    receiver_name = config.get(section, 'receiver_name')
                    receiver_address = config.get(section, 'receiver_address')
                    recipients.append([receiver_name, receiver_address])
                folder_ok.append([folder, recipients, files, folder_path])       #folder_ok列表中的元素为[[子文件夹名称],[子文件夹中的config.ini文件中的内容],[子文件夹中的文件列表]]

    if not args.sender:
        # 输出folder_ok列表中的内容
        for folder_info in folder_ok:
            print('\n'.join(folder_info[0]))            # 文件夹名
            recipients_str = " | ".join([",".join(recipient) for recipient in folder_info[1]])
            print(recipients_str)                       # 收件人名称和邮箱地址
            ''' 一行一个
            for recipient in folder_info[1]:
                print(','.join(recipient))
            '''
            print(','.join(folder_info[2]))             # 第三个元素是附件
            print(folder_info[3])             # 第四个元素是路径，有双反斜杠
            print('----\n')

        print('以下目录中没有config.ini文件-收件人')
        # 输出folder_no中的元素
        print('、'.join(folder_no))
        print("----")
        print(folder_ok)
    else:
        config = read_config()
        sender_name = config.get('sender', 'sender_name')
        sender_address = config.get('sender', 'sender_address')
        server = {
            'smtp_server': config.get('server', 'smtp_server'),
            'smtp_port': config.get('server', 'smtp_port'),
            'smtp_ssl': config.get('server', 'smtp_ssl'),
            'smtp_user': config.get('server', 'smtp_user'),
            'smtp_password': config.get('server', 'smtp_password')
        }



        log_file_path = os.path.abspath('log.log')  # 获取日志文件的绝对路径

        logger.add(log_file_path, rotation="500 MB")  # 添加日志文件输出器，并进行日志文件的自动分割

        error_found = False  # 用于标记是否存在错误

        for folder_info in folder_ok:
            folder_name = folder_info[0][0]         # 子文件夹名称
            recipients = folder_info[1]             # 收件人信息，名称和邮箱
            files_names = folder_info[2]            # 附件
            folder_path = folder_info[3]            # 文件夹路径

            os.chdir(folder_path)

            for recipient in recipients:
                receiver_name = recipient[0]           # 收件人名称
                receiver_address = recipient[1]        # 收件人地址
                subject = config.get('body', 'subject')        # 主题
                content = config.get('body', 'content')         # 内容

                logger.info(f'发送邮件给 {receiver_name} ({receiver_address}) 从文件夹获取 {folder_name}...')

                try:
                    send_email(server, f'{sender_name} <{sender_address}>', f'{receiver_name} <{receiver_address}>',
                            subject, content, files_names)  # 传递文件名列表作为附件参数
                    logger.info(f'{folder_name}邮件发送成功')
                except Exception as e:
                    logger.error(f'{folder_name}邮件发送失败：代码: {str(e)}')
                    error_found = True  # 标记存在错误

        if error_found:
            print("发送邮件存在错误，请查看日志文件log.log")
        else:
            print("未发现错误")



        print('所有邮件已发送完成!')

if __name__ == '__main__':
    main()
