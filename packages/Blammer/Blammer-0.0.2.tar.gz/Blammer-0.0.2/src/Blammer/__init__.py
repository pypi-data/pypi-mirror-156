from getpass import getpass
import turtle
import logging
import password

def your_help():
    print('Enter your form help')
    helpic = input('Help > ')
    print(helpic)

def help():
    print("your_help() = Enter your help and be showed")
    print("screen(size_width, size_height) = Create a screen")

def screen(size_width, size_height):
    turtle = turtle.Turtle()
    turtle.screensize(size_width, size_height)

def chat():
    username = input('Enter username : ')
    getpass('Enter your password : ')    
    print("Stephen > Hello", (username), "!")
    message = input("Tap your message here >")
    while message == "Hi!":
        print("Stephen > What are you doing now ?")
        message = input("Tap your message here >")
        if not message == "Nothing":
            print("Ok, Bye!")
            print("Stephen has Quited The Chat")
        if message == "Nothing":
            print("Stephen > No, You chat with me")
            message = input("Tap your message here >")

chat()