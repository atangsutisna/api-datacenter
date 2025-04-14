# from myfile import get_user_age
import myfile

# print("What's going on")
try:
    myfile.get_user_age()
except ValueError:
    print("That is not valid value for your age")
