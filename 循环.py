#for循环
# range(2,8,2)    #range(开始（包含），结束（不包含），步长）    2 4 6
# range(8,2,-2)   #the same
# for i in range(2,8,2) :
#     print(i)
# for i in 'Python' :
#     print(i)
# for _ in range(5) :(若i=—_,则括号内的5表示重复5次）
#     print('Python')
# num=int(input('请输入一个数字'))
# print(f'{num}以内的偶数有......')
# for i in range(num+1):
#      if i % 2 ==0 :
#          print(i,end=',')
# for i in range(0,num+1,2):
#      print(i,end=',')
# num=1
# #while 循环
# while num<=10:
#     print(num)
#     num+=1
# else:
#     print('while循环正常执行结束后打印的内容')
# print('无论while是否正常执行都会打印的内容')
# save_pwd='123456'
# pwd=''
# chance=3
# input('请输入您的密码：')
# while pwd != save_pwd and chance>0:
#     pwd=input('密码错误！请再次输入你的密码：')
#     chance-=1
# if pwd==save_pwd:
#     print('登录成功！')
# else:
#     print('您的次数已用完，请稍后再试'
# for i in range(10):
#     if i==3:
#         continue    #只跳过这一个数
#     print(i)
# for i in range(10):
#     if i==3:
#         break       #此后的数都不打印
#     print(i)
save_pwd='123456'
all_continue=False
for _ in range(3):
    pwd=input('请输入您的密码：')
    if pwd==save_pwd:
        print('密码正确！登录成功！')
        break
    else:
        print('密码错误!')
        all_continue=True
        continue
if all_continue:
    print('您的次数已用光，请一段时间后重试')

