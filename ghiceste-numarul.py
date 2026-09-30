import random
nu = random. randint(1,10)

#print (nu)
print("numar aleator")

while True:
    try:
        guess = int(input ("introdu numarul:  "))
           
        if guess<nu:
            print("too low")
        elif guess>nu:
            print("too high")
        else:
            print("ai gichit😃")
            break

    except ValueError:
        print ("eroare")
