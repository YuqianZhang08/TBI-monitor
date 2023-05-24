def quick_sort(arr):
    if len(arr)<=1:
        return arr
    middlearr=arr[len(arr)//2]
    left=[]
    right=[]
    equal=[]
    for x in arr:
        if x>middlearr:
            left.append(x)
        elif x < middlearr:
            right.append(x)
        elif x==middlearr:
            equal.append(x)
    return quick_sort(left)+equal+quick_sort(right)

arr=[10,8,5,6]

quick_sort(arr)
