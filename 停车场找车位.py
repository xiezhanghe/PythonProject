free=None
for i in range(1,6):
    if i < 5 and i!=free:
        continue
    elif i==free and i<=5:
        print('已成功为您找到车位！', i, '车位空闲')
        break
    elif i==5 and i!=free:
        print('车位已满')


