# Student Info management System

import os
import sqlite3
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
from tkinter.messagebox import *
from tkinter.simpledialog import askstring


class LoginPage:
    """the login interface class"""

    def __init__(self, master):
        self.root = master # set the root window
        self.root.title('login') # interface's title
        self.root.geometry('400x200+600+300') # set the login page's size
        self.root.title('')
        self.conn = sqlite3.connect('mydb.db') # connect the database
        ## use tk.StringVar() to receive the type in from keyboard
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.page = tk.Frame(self.root)
        self.creatapage() # creat the page which we will see

    def creatapage(self):
        """layout the page"""
        tk.Label(self.page).grid(row=0) # tk.Label can creat a label with text in it
        tk.Label(self.page, text='username:').grid(row=1, stick=tk.W, pady=10) # tk.W means put the label on the west of the window; pady means set a interval
        tk.Entry(self.page, textvariable=self.username).grid(row=1, column=1, stick=tk.E) # tk.Entry can creat input box; tk.E put the label on the east of the window
        tk.Label(self.page, text='password:').grid(row=2, stick=tk.W, pady=10)
        tk.Entry(self.page, textvariable=self.password, show='*').grid(row=2, stick=tk.E, column=1)
        tk.Button(self.page, text='login', command=self.login).grid(row=3, stick=tk.W, pady=10) # parameter command can bind a function, when we push the button
        tk.Button(self.page, text='sign up', command=self.register).grid(row=3, stick=tk.E, column=1)
        self.page.pack()

    def login(self):
        """the login function"""
        curs = self.conn.cursor() # used to search and modify in the database
        query = "select username, password, type, id from loginuser where username='%s'" % self.username.get() 
        curs.execute(query)  # return a iterator, including all information which's user name equals to that given in the entry box 
        c = curs.fetchall()  # store all information searched from database
        if len(c) == 0: # the search rusult's length is 0, means no required information stored in database
            messagebox.showerror('sign in failed', 'The account does not exist')
        else:
            us, pw, type, id = c[0]
            if us == self.username.get() and pw == self.password.get(): # the username and password are both true
                self.conn.close() # disconnect the database
                messagebox.showinfo('Login successfully', 'Welcome: %s' % us)
                self.page.destroy()
                if type=="admin":
                    MainUI_admin(self.root) # go to admin's main interface
                elif type=="teacher":
                    MainUI_teacher(self.root) # go to teacher's main interface
                else:
                    con = sqlite3.connect("mydb.db") 
                    cur = con.cursor()
                    cur.execute("select * from studentUser") # import all students' id, for linking the account with student's id
                    studentList = cur.fetchall()
                    cur.close()
                    con.close() 
                    if id==-1: # if this account is new
                        id_given =  int(askstring("Attention","Please input your id to linked your account")) # input the student's id that your account want to link to
                        flag = 0
                        for i in range(len(studentList)):
                            for item in studentList[i]:
                                if id_given == item:
                                    flag = 1
                                    break
                        if flag == 1: # find the id you want to link
                            con = sqlite3.connect("mydb.db")
                            cur = con.cursor()
                            cur.execute("update loginuser set id = ? where username = ?",(id_given,us))
                            id = id_given
                            con.commit()
                            cur.close()
                            con.close()
                        else: # the id inputed to link isn't existed
                            messagebox.showerror("Login failed","Your given id isn't existed")
                            self.creatapage()
                            return
                    else: # check your linked id whether be deleted
                        flag = 0
                        for i in range(len(studentList)):
                            for item in studentList[i]:
                                if id == item:
                                    flag = 1
                                    break
                        if flag==0:
                            messagebox.showerror("Login failed","Your account had been deleted, please contact the administor")
                    MainUI_student(id,self.root) # go to student's interface
            else:
                messagebox.showwarning('Login failed', 'Password error')

    def register(self):
        """go to register interface"""
        self.conn.close()
        self.page.destroy()
        RegisterPage(self.root) # go to register interface


class RegisterPage:
    """the sign up interface"""

    def __init__(self, master=None):
        self.root = master
        self.root.title('Sign up')
        self.root.geometry('400x250')
        self.conn = sqlite3.connect('mydb.db')
        self.username = tk.StringVar()
        self.password0 = tk.StringVar()  # enter the password twice
        self.password1 = tk.StringVar()  
        self.page = tk.Frame(self.root)
        self.createpage()

    def createpage(self):
        """page lay out"""
        # layout the register interface
        tk.Label(self.page).grid(row=0)
        tk.Label(self.page, text="username:").grid(row=1, stick=tk.W, pady=10)
        tk.Entry(self.page, textvariable=self.username).grid(row=1, column=1, stick=tk.E)
        tk.Label(self.page, text="password:").grid(row=2, stick=tk.W, pady=10)
        tk.Entry(self.page, textvariable=self.password0, show='*').grid(row=2, column=1, stick=tk.E)
        tk.Label(self.page, text="confirm the password:").grid(row=3, stick=tk.W, pady=10)
        tk.Entry(self.page, textvariable=self.password1, show='*').grid(row=3, column=1, stick=tk.E)
        tk.Button(self.page, text="go back", command=self.repage).grid(row=4, stick=tk.W, pady=10)
        tk.Button(self.page, text="register", command=self.register).grid(row=4, column=1, stick=tk.E)
        self.page.pack()

    def repage(self): # refresh the interface if sign up failed
        """go back to the login page"""
        self.page.destroy()
        self.conn.close()
        LoginPage(self.root)

    def register(self): 
        """register function"""
        if self.password0.get() != self.password1.get(): # passwords input twicely don't match
            messagebox.showwarning('Error', 'The two passwords do not match')
        elif len(self.username.get()) == 0 or len(self.password0.get()) == 0: # username or password is null
            messagebox.showerror("Error", "Input is null")
        else:
            curs = self.conn.cursor()
            query = 'insert into loginuser values (?,?,?,?)' # insert the account's information you register into database
            val = [self.username.get(), self.password0.get(),"student",-1]
            try:
                curs.execute(query, val)
                self.conn.commit()
                self.conn.close()
                messagebox.showinfo("Success", "Register successfully, Press OK to return")
                self.page.destroy()
                LoginPage(self.root)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "This account is exist") # if the username exists, error will happen when insert it into database


class MainUI_admin:
    """admin's control panel"""

    def __init__(self, master=None):
        self.root = master
        self.dbstr = "mydb.db"
        self.root.geometry('700x700+300+50')
        self.root.title('Student management system - admin')
        self.sid = tk.StringVar()      # ID
        self.name = tk.StringVar()     # Name
        self.sex = tk.StringVar()  # gender
        self.age = tk.StringVar()  # age
        self.score = tk.StringVar()    # score
        self.clickedStudentNumber = "No selected"   # used to recorded the clicked student's id
        self.dataTreeview = ttk.Treeview(self.root, show='headings', column=('sid', 'name', 'sex','age','score')) # display strudents' information in columns
        self.createPage()

    def showAllInfo(self):
        """Show all student's information"""
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item) # clear the box displaying all students' informatino
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        lst = cur.fetchall()
        for item in lst:
            self.dataTreeview.insert("", 1, text="line1", values=item)
        cur.close()
        con.close()


    def appendInfo(self):
        """Add student's information"""
        # if any information is null, error will rise up
        if self.sid.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.name.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.sex.get()== 0:
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.age.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.score.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        else:
            x = self.dataTreeview.get_children()
            for item in x:
                self.dataTreeview.delete(item)
            list1 = [] # dump all information will add into a list
            list1.append(self.sid.get())
            list1.append(self.name.get())
            list1.append(self.sex.get())
            list1.append(self.age.get())
            list1.append(self.score.get())
            con = sqlite3.connect(self.dbstr)
            cur = con.cursor()
            cur.execute("insert into studentUser values(?,?,?,?,?)", tuple(list1)) # insert the new information into the database
            con.commit()
            cur.execute("select * from studentUser")
            lst = cur.fetchall()
            for item in lst:
                self.dataTreeview.insert("", 1, text="line1", values=item)
            cur.close()
            con.close()

    def deleteInfo(self):
        """delete student's infomation"""
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        studentList = cur.fetchall()
        cur.close()
        con.close()
        num = self.clickedStudentNumber
        flag = 0
        if not num.isnumeric(): # don't click any student
            showerror(title='Attention', message='Delete failed, don\'t choose any student')
            return
        for i in range(len(studentList)): # seach the student you want to delete
            for item in studentList[i]:
                if int(num) == item:
                    flag = 1
                    con = sqlite3.connect(self.dbstr)
                    cur = con.cursor()
                    cur.execute("delete from studentUser where id = ?", (int(num),))
                    con.commit()
                    cur.close()
                    con.close()
                    break
        if flag == 1:
            showinfo(title='Attention', message='Delete successfully')
            self.clickedStudentNumber = "No selected"
        else:
            showerror(title='Attention', message='Delte failed')
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item)
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        lst = cur.fetchall()
        for item in lst:
            self.dataTreeview.insert("", 1, text="line1", values=item)
        cur.close()
        con.close()

    def modifyInfo(self):
        "modify student's info"
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        studentList = cur.fetchall()
        cur.close()
        con.close()
        print(self)
        print(studentList)
        num = self.clickedStudentNumber
        flag = 0
        if not num.isnumeric():
            showerror(title='Attention', message='Modify failed, don\'t choose any student')
            return
        for i in range(len(studentList)): # search the student you want to modify
            for item in studentList[i]:
                if int(num) == item:
                    flag = 1
                    con = sqlite3.connect(self.dbstr)
                    cur = con.cursor()
                    new_score = askstring("Update student's score","New score")
                    cur.execute("update studentUser set score = ? where id = ?", (int(new_score),int(num)))
                    con.commit()
                    cur.close()
                    con.close()
                    break
        if flag == 1:
            showinfo(title='Attention', message='Modify successfully')
            self.clickedStudentNumber = "No selected"
        else:
            showerror(title='Attention', message='Modify failed')
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item)
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        lst = cur.fetchall()
        for item in lst:
            self.dataTreeview.insert("", 1, text="line1", values=item)
        cur.close()
        con.close()

    def getClickedStudentNumber(self,event):  # get the id of the clicked student
        self.clickedStudentNumber = self.dataTreeview.item(self.dataTreeview.selection()[0],"values")[0]
        print("You click a student, his/her id is: ",str(self.clickedStudentNumber))

    def createPage(self):
        """Page layout"""
        con = sqlite3.connect('mydb.db')
        cur = con.cursor()
        self.sex = tk.StringVar()
        self.sex.set("Male")

        tk.Label(self.root, text="ID:").place(relx=0, rely=0.05, relwidth=0.1)
        tk.Label(self.root, text="Name:").place(relx=0.5, rely=0.05, relwidth=0.1)
        tk.Label(self.root, text="Score:").place(relx=0, rely=0.1, relwidth=0.1)
        tk.Label(self.root, text="Age:").place(relx=0.5,rely=0.1,relwidth=0.1)
        tk.Radiobutton(self.root, text='Male', variable=self.sex, value="Male").place(relx=0.75, rely=0.1, relwidth=0.1)
        tk.Radiobutton(self.root, text='Female', variable=self.sex, value="Female").place(relx=0.85, rely=0.1, relwidth=0.1)
        tk.Entry(self.root, textvariable=self.sid).place(relx=0.1, rely=0.05, relwidth=0.37, height=25)
        tk.Entry(self.root, textvariable=self.name).place(relx=0.6, rely=0.05, relwidth=0.37, height=25)
        tk.Entry(self.root, textvariable=self.score).place(relx=0.1, rely=0.1, relwidth=0.37, height=25)
        tk.Entry(self.root, textvariable=self.age).place(relx=0.6, rely=0.1, relwidth=0.15, height=25)
        tk.Label(self.root, text='Student Information Management System', bg='white', fg='red', font=('Times', 15)).pack(side=tk.TOP, fill='x')
        tk.Button(self.root, text="Show all", command=self.showAllInfo).place(relx=0.2, rely=0.2, width=100)
        tk.Button(self.root, text="Add", command=self.appendInfo).place(relx=0.4, rely=0.2, width=100)
        tk.Button(self.root, text="delete", command=self.deleteInfo).place(relx=0.6, rely=0.2, width=100)
        tk.Button(self.root, text="modify", command=self.modifyInfo).place(relx=0.8, rely=0.2, width=100)
        self.dataTreeview.column('sid', width=100, anchor="center")
        self.dataTreeview.column('name', width=100, anchor="center")
        self.dataTreeview.column('sex', width=100, anchor="center")
        self.dataTreeview.column('age', width=100, anchor="center")
        self.dataTreeview.column('score', width=100, anchor="center")
        self.dataTreeview.heading('sid', text='ID')
        self.dataTreeview.heading('name', text='Name')
        self.dataTreeview.heading('sex', text='Gender')
        self.dataTreeview.heading('age', text='Age')
        self.dataTreeview.heading('score', text='Score')
        self.dataTreeview.place(rely=0.3, relwidth=0.97)
        self.dataTreeview.bind('<ButtonRelease-1>',self.getClickedStudentNumber)
        self.showAllInfo()

class MainUI_teacher:
    """teacher's control panel"""

    def __init__(self, master=None):
        self.root = master
        self.dbstr = "mydb.db"
        self.root.geometry('700x700+300+50')
        self.root.title('Student management system - teacher')
        self.sid = tk.StringVar()      # ID
        self.name = tk.StringVar()     # Name
        self.sex = tk.StringVar()  # gender
        self.age = tk.StringVar()  # age
        self.score = tk.StringVar()    # score
        self.clickedStudentNumber = "No selected"   # used to recorded the clicked student's id
        self.dataTreeview = ttk.Treeview(self.root, show='headings', column=('sid', 'name', 'sex','age','score')) # display strudents' information in columns
        self.createPage()

    def showAllInfo(self):
        """Show all student's information"""
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item)
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        lst = cur.fetchall()
        for item in lst:
            self.dataTreeview.insert("", 1, text="line1", values=item)
        cur.close()
        con.close()

    def modifyInfo(self):
        "modify student's info"
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        studentList = cur.fetchall()
        cur.close()
        con.close()
        print(self)
        print(studentList)
        num = self.clickedStudentNumber
        flag = 0
        if not num.isnumeric():
            showerror(title='Attention', message='Modify failed, don\'t choose any student')
            return
        for i in range(len(studentList)):
            for item in studentList[i]:
                if int(num) == item:
                    flag = 1
                    con = sqlite3.connect(self.dbstr)
                    cur = con.cursor()
                    new_score = askstring("Update student's score","New score")
                    cur.execute("update studentUser set score = ? where id = ?", (int(new_score),int(num)))
                    con.commit()
                    cur.close()
                    con.close()
                    break
        if flag == 1:
            showinfo(title='Attention', message='Modify successfully')
            self.clickedStudentNumber = "No selected"
        else:
            showerror(title='Attention', message='Modify failed')
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item)
        con = sqlite3.connect(self.dbstr)
        cur = con.cursor()
        cur.execute("select * from studentUser")
        lst = cur.fetchall()
        for item in lst:
            self.dataTreeview.insert("", 1, text="line1", values=item)
        cur.close()
        con.close()

    def getClickedStudentNumber(self,event):  # get the id of the clicked student
        self.clickedStudentNumber = self.dataTreeview.item(self.dataTreeview.selection()[0],"values")[0]
        print("You click a student, his/her id is: ",str(self.clickedStudentNumber))

    def createPage(self):
        """Page layout"""
        con = sqlite3.connect('mydb.db')
        cur = con.cursor()
        self.sex = tk.StringVar()
        self.sex.set("Male")

        tk.Label(self.root, text='Student Information Management System', bg='white', fg='red', font=('Times', 15)).pack(side=tk.TOP, fill='x')
        tk.Button(self.root, text="Show all", command=self.showAllInfo).place(relx=0.2, rely=0.2, width=100)
        tk.Button(self.root, text="modify", command=self.modifyInfo).place(relx=0.8, rely=0.2, width=100)
        self.dataTreeview.column('sid', width=100, anchor="center")
        self.dataTreeview.column('name', width=100, anchor="center")
        self.dataTreeview.column('sex', width=100, anchor="center")
        self.dataTreeview.column('age', width=100, anchor="center")
        self.dataTreeview.column('score', width=100, anchor="center")
        self.dataTreeview.heading('sid', text='ID')
        self.dataTreeview.heading('name', text='Name')
        self.dataTreeview.heading('sex', text='Gender')
        self.dataTreeview.heading('age', text='Age')
        self.dataTreeview.heading('score', text='Score')
        self.dataTreeview.place(rely=0.3, relwidth=0.97)
        self.dataTreeview.bind('<ButtonRelease-1>',self.getClickedStudentNumber)
        self.showAllInfo()

class MainUI_student:
    """student's control panel"""

    def __init__(self, id,master=None):
        self.root = master
        self.root.title('Student management system - student')
        self.new_sex = tk.StringVar()
        self.new_age = tk.StringVar()
        self.id = int(id)
        self.showInfo()

    def getInfo(self):
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("select * from studentUser where id=?",(self.id,))
        self.name, self.sex, self.age, self.score = cur.fetchall()[0][1:]
        cur.close()
        con.close()

    def showInfo(self):
        """Page layout"""
        self.getInfo()
        self.root.geometry('550x200')
        self.page = tk.Frame(self.root)
        tk.Label(self.page, text="ID: %s" %self.id).grid(row=1,column=1,padx=20,pady=20)
        tk.Label(self.page, text="Name: %s" %self.name).grid(row=1,column=2,padx=20,pady=20)
        tk.Label(self.page, text="Age: %s" %self.age).grid(row=1,column=3,padx=20,pady=20)
        tk.Label(self.page, text="Gender: %s" %self.sex).grid(row=2,column=1,padx=20,pady=20)
        tk.Label(self.page, text="Score: %s" %self.score).grid(row=2,column=2,padx=20,pady=20)
        tk.Button(self.page, text='modify', command=self.modify).grid(row=2,column=3,padx=20,pady=20)

        self.page.pack()

    def modify(self):
        self.page.destroy()
        self.root.geometry('600x250')
        self.page = tk.Frame(self.root)

        self.new_sex.set(self.sex)
        tk.Label(self.page, text="ID: %s" %self.id).grid(row=1,column=1,padx=20,pady=20)
        tk.Label(self.page, text="Name: %s" %self.name).grid(row=1,column=2,padx=20,pady=20)
        tk.Label(self.page, text="Score: %s" %self.score).grid(row=1,column=3,padx=20,pady=20)
        tk.Label(self.page, text="Age:").grid(row=2,column=1,padx=5,pady=20)
        tk.Entry(self.page,textvariable=self.new_age).grid(row=2,column=2,padx=20,pady=20)
        tk.OptionMenu(self.page, self.new_sex, 'Male', 'Female').grid(row=2,column=3,padx=20,pady=20)
        tk.Button(self.page, text='commit', command=self.commit).grid(row=3,column=1,padx=40,pady=20)
        tk.Button(self.page, text='undo', command=self.undo).grid(row=3,column=2,padx=40,pady=20)

        self.page.pack()

    def commit(self):
        """commit the modify"""
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("update studentUser set sex = ? where id = ?",(self.new_sex.get(),self.id))
        cur.execute(f"update studentUser set age = {self.new_age.get()} where id = {self.id}")
        con.commit()
        cur.close()
        con.close()
        self.page.destroy() # after commit the modify, destroy the page then reload student's interface
        self.showInfo()


    def undo(self):
        """undo the modify"""
        self.page.destroy()
        self.showInfo()

if __name__ == '__main__':
    if os.path.exists("mydb.db") is not True: # if database is not exist, we creat it
        fp = open("mydb.db","w")
        fp.close()
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        # initialization the database
        cur.execute('CREATE TABLE IF NOT EXISTS loginuser (username varchar(30) primary key, password varchar(30), type varchar(20),id int(10))')
        cur.execute('create table if not exists studentUser(id int(10) primary key,name varchar(20),sex char(2), age int(10), score int(10))')
        cur.execute("insert into loginuser values(?,?,?,?)",['admin','admin','admin',-1])
        cur.execute("insert into loginuser values(?,?,?,?)",['teacher','teacher','teacher',-1])
        con.commit()
        cur.close()
        con.close()
    root = tk.Tk() # creat a root window
    LoginPage(root) # Loading the Login Page
    root.mainloop() # Doing loop to execute the program