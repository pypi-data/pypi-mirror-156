def filehandler():
    print("Note : Open the file file using choice 0 then start working on your file.")
    option="y"
    while option=='y':
        print('0. Open')
        print('1. FileInfo')
        print('2. Write')
        print('3. Read')
        print('4. Append')
        print('5. Close')
        ch = int(input('Enter Your Choice : '))
        if ch == 0:
            filename=input("Enter File Name : ")
            mode=input("Enter mode (r/w/a/r+/w+/a+): ")
            f=open(filename,mode)
        elif ch == 1:
            print("Name : ",f.name)
            print("Mode : ",f.mode)
            print("Encoding : ",f.encoding)
        elif ch == 2:
            f.close()
            f=open(filename,'r+')
            written_no=int(input('How many lines to be written ?'))
            for i in range(written_no):
                write=input("Enter the Data : ")
                f.writelines(write)
            f.close()
            f=open(filename,mode)
        elif ch == 3:
            f.close()
            f=open(filename,'r')
            txt=f.read()
            print(txt)
            f.close()
            f=open(filename,mode)
        elif ch == 4:
            f.close()
            f=open(filename,'a+')
            written_no=int(input('How many lines to be written ?'))
            for i in range(written_no):
                append=input("Enter the Data : ")
                f.write(append)
            f.close()
            f=open(filename,mode)
        elif ch == 5:
            f.close()
            print("File Closed Successfully")
        else:
            print("Wrong option")
        option=input("Do You want to continue ? (y/n) :")
        if option=='y':
            continue
        else :
            break
