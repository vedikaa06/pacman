empty_set=set()
set1= {"green","red","blue","red"}
print(set1)

set2=set({7,1,2,23,2,4,5})
print(set2)

print("is red in set1?","red" in set1)

print("length is", len(set2))
print("max is ", max(set2))
print("min is", min(set2))
print("sum is", sum(set2))

set3=set1|({"green","yello"})
print(set3)

set3=set1-{"green","yellow"}
print(set3)

set3=set1 & {"green","yellow"}
print(set3)

set3= set1^{"green","yellow"}
print(set3)

