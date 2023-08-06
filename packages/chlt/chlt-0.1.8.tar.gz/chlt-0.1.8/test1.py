a = '寒'.encode("utf-8").hex()
b =ord('寒')
c = hex(b)
print('5bd2')
# a.replace('\u','')
print(c[2:])
print(type(c))
url = 'https://strokeorder.com.tw/bishun-animation/662f-stroke-order.gif'

c = url.split("/")[-1].replace('-stroke-order','')
print(c)
