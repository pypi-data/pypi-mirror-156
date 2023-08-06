# Function to demonstrate printing pattern of alphabets
def pyalphat(n):
     """ this function print triangle shape alphabet by asigning numeric number
     """
    # initializing value corresponding to 'A'
    # ASCII value
     num = 65
 
    # outer loop to handle number of rows
    # 5 in this case
     for i in range(0, n):
     
        # inner loop to handle number of columns
        # values changing acc. to outer loop
        for j in range(0, i+1):
         
            # explicitely converting to char
            ch = chr(num)
         
            # printing char value
            print(ch, end=" ")
     
        # incrementing number
        num = num + 1    ## ==>indentation to outer loop
     
        # ending line after each row
        print("\r")