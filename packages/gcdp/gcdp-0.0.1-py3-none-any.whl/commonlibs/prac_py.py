# 11 Tips And Tricks To Write Better Python Code
# Refeneces. https://www.youtube.com/watch?v=8OKTAedgFYg

# 1. range(len(x))보다 enumerate(x)를 사용하자
data = [2,1,10, -1]
for i in range(len(data)):
    if data[i] < 0:
        print("neg")
    else:
        print("pos")

for indx, d in enumerate(data):
    if d < 0:
        print("neg")
    else:
        print("pos")
# 2. for loop보다 list comprehension을 사용하자.
import time
sq = []

start = time.time()
for i in range(0, 10000):
    sq.append(i*i)
end = time.time()
print(end - start)

start = time.time()
sq = [i*i for i in range(0, 10000)]
end = time.time()
print(end - start)

# - 3. 복잡한 리스트를 반복할때 sorted()함수를 사용하자 즉, 먼저 sort하고 iterate하자
data  =[{"name":"kelly", "age":15}, {"name":"esther", "age":5}, {"name":"John", "age":43}]
sorted_data = sorted(data, key=lambda x:x["age"], reverse=True)
print(sorted_data)


# unique한 값들은 set에 저장하자.

# generator를 사용하여 메모리의 낭비를 줄이자. - generator 목적 자체도 메모리를 효율적으로 사용하기 위함
import sys

my_list = [i for i in range(0, 1000)]
print(type(my_list))
print(sum(my_list))
print(sys.getsizeof((my_list)), "bytes")
#  오잉 set타입인줄 착각 거의 메모리가 거의 80배이상 차이남?
my_gen = (i for i in range(0, 1000))
print(type(my_gen))
print(sum(my_gen))
print(sys.getsizeof((my_gen)), "bytes")

# dict형의 default값을 get 함수나 setdefault함수를 이용하여 정의하자.

# 10. dict형을 합칠때 **d1 **d2를 활용하자. (Python 3.5이상)
d1 = {"name":"kelly", "age":15}
d2 = {"name":"kelly", "city":"Monterey"}
merged_dict = {**d1, **d2}
print(merged_dict)

# 11.  if x in [1,2,3,4]를 이용하여 if문을 간소화하자
color = ["red", "green", "blue"]
c="red"
if c =="red" or c=="green" or c=="blue":
    print(c, "is main color")
if c in color:
    print(c, "is main color")

#12. 현재달
from datetime import date
today = date.today().strftime("%m")
print(int(today))