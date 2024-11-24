def isPalindrome( x: int) -> bool:
        num = str(x)
        rev_num = ''
        for i in range(len(num)-1, -1, -1):
            rev_num += num[i]
        return num == rev_num

# print(isPalindrome(121))


def twoSum(nums, target):
      counter = nums[0]
      result_idx = [0]
      for i in range(1, len(nums)-1):
            counter += nums[i]
            print("Before :", counter, i, nums[1])
            result_idx.append(i)
            if counter == target:
                return result_idx 
            else:
                  counter -= nums[i]
                  print("Before :", counter, i, nums[1])
                  continue
            

print(twoSum([3,2,4], 6))