a = [8, 10, 12, 9, 8, 10, 12, 14, 11]
result_array = [0 for i in range(len(a))]

result_array[0] = 1

for index in range(len(a)):
	if index != 0:
		if a[index] > a[index - 1]:
			result_array[index] = result_array[index - 1] + 1
		else:
			result_array[index] = 1


answer = max(result_array)