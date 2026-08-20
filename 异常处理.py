try:
    cups=int(input('想要几杯咖啡呢'))
    if cups<0:
        print('为你准备',cups,'杯咖啡哦~')
    else:
        print('请至少输入一杯哦')
except ValueError:
    print('请输入整数哦~')