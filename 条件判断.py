total_price=250
if total_price>=300:
    total_price*=0.7
elif total_price>=200:
    total_price*=0.8
elif total_price>=100:
    total_price*=0.9
else:
    total_price=total_price

print('total_price:',total_price)

