import random
def tables():

    num1 = random.randint(2, 12)
    num2 = random.randint(2, 12)
    print("What is ", end='')
    print(num1, end='')
    print(" x ", end='')
    print(num2, end='')
    print("? ", end='')
    answer = num1*num2
    
    inp = input()
    
    
    while int(inp) != answer:
        print("Incorrect - try again.")
        inp = input()
        
    print("Correct!")
 
tables()
