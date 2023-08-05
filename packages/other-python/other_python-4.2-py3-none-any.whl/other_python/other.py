import random
def middle(min: int,max: int):
 return (min+max)/2
def change(number: int,change: int):
    return number+random.randint(-change,change)
def ListToInt(List:list) :
    result = 0
    for x in List:
         result += x
    return result
ud={}
def up_down(key,min:int=0,max:int=100,change_by:int=1):
 try:
   ud[key]
 except:
   ud[key]=[min,max,0,"+"]
 if ud[key][3]=="+":
  if not ud[key][2]>=ud[key][1]:
     ud[key][2]+=change_by
  else:
    ud[key][2]-=change_by
    ud[key][3]="-"
 elif ud[key][3]=="-":
  if not ud[key][2]<=ud[key][0]:
     ud[key][2]-=change_by
  else:
    ud[key][2]+=change_by
    ud[key][3]="+"
 return ud[key][2]