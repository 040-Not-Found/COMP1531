from numpy import prod
import string


if __name__ == '__main__':
    my_list = []

    #a to e
    for i in string.ascii_lowercase[:5]:
        print("Enter " + i + ": ", end = '')
        my_list.append(int(input()))

    #print the minimum number in my_list
    print("Minimum: " + str(min(my_list)))

    #print the product of the first 4 numbers in my_list
    print("Product of first 4 numbers: " + str(prod(my_list[:4])))

    #print the product of the last 4 numbers in my_list
    print("Product of last 4 numbers: " + str(prod(my_list[-4:])))
