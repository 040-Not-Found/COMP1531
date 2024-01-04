def check_password(password):
    '''
    Takes in a password, and returns a string based on the strength of that password.

    The returned value should be:
    * "Strong password", if at least 12 characters, contains at least one number, at least one uppercase letter, at least one lowercase letter.
    * "Moderate password", if at least 8 characters, contains at least one number.
    * "Poor password", for anything else
    * "Horrible password", if the user enters "password", "iloveyou", or "123456"
    '''

    
    if (len(password) >= 12 and 
    any(x.isupper() for x in password) and 
    any(x.islower() for x in password)):
        check = "Strong password"
        print(check)
        return check
        
    elif (len(password) >= 8 and 
    any(x.isdigit() for x in password)):
        check = "Moderate password"
        print(check)
        return check
        
    elif (password == "password" or 
        password == "123456" or 
        password == "iloveyou"):
        check = "Horrible password"
        print(check)
        return check
        
    else:
        check = "Poor password"
        print(check)
        return check
    
    pass
'''    
if __name__ == '__main__':
    print(check_password("ihearttrimesters"))
    # What does this do?
    This is will print "Poor password"
'''

#check_password("passwordqwqrwere")
