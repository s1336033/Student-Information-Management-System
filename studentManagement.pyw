# Student Information Management System

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
        self.root = master  
        self.root.title('Student Information Management System')  
        self.root.geometry('500x200+600+300')  
        self.conn = sqlite3.connect('mydb.db')  
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.page = tk.Frame(self.root)
        self.creatapage()  

    def creatapage(self):
        """layout the page"""
        tk.Label(self.page).grid(row=0)  
        tk.Label(self.page, text='username:').grid( row=1, stick=tk.W, pady=10)  
        tk.Entry(self.page, textvariable=self.username).grid(row=1, column=1, stick=tk.E)  
        tk.Label(self.page, text='password:').grid(row=2, stick=tk.W, pady=10)
        tk.Entry(self.page, textvariable=self.password,show='*').grid(row=2, stick=tk.E, column=1)
        tk.Button(self.page, text='login', command=self.login).grid(row=3, stick=tk.W, pady=10)  
        tk.Button(self.page, text='sign up',command=self.register).grid(row=3, stick=tk.E, column=1)
        self.page.pack()

    def login(self):
        """the login function"""
        curs = self.conn.cursor()  
        query = "select username, password, type, id from loginuser where username='%s'" % self.username.get()  
        curs.execute(query)  
        c = curs.fetchall()  
        if len(c) == 0:  
            messagebox.showerror('sign in failed','The account does not exist')
        else:
            us, pw, type, id = c[0]
            if us == self.username.get() and pw == self.password.get( ):  
                self.conn.close()  
                messagebox.showinfo('Login successfully', 'Welcome: %s' % us)
                self.page.destroy()
                if type == "admin":
                    MainUI_admin(self.root)  
                elif type == "teacher":
                    MainUI_teacher(self.root)  
                else:
                    con = sqlite3.connect("mydb.db")
                    cur = con.cursor()
                    cur.execute("select * from studentUser")  
                    studentList = cur.fetchall()
                    cur.close()
                    con.close()
                    if id == -1:  
                        id_given = int(askstring("Attention", "Please input your id to linked your account"))  
                        flag = 0
                        for i in range(len(studentList)):
                            for item in studentList[i]:
                                if id_given == item:
                                    flag = 1
                                    break
                        if flag == 1:  
                            con = sqlite3.connect("mydb.db")
                            cur = con.cursor()
                            cur.execute("update loginuser set id = ? where username = ?",(id_given, us))
                            id = id_given
                            con.commit()
                            cur.close()
                            con.close()
                        else:  
                            messagebox.showerror("Login failed", "Your given id isn't existed")
                            self.creatapage()
                            return
                    else:  
                        flag = 0
                        for i in range(len(studentList)):
                            for item in studentList[i]:
                                if id == item:
                                    flag = 1
                                    break
                        if flag == 0:
                            messagebox.showerror("Login failed", "Your associated student had been deleted, please contact the administor" )
                            self.creatapage()
                            return
                    MainUI_student(id, self.root)  
            else:
                messagebox.showwarning('Login failed', 'Password error')

    def register(self):
        """go to register interface"""
        self.conn.close()
        self.page.destroy()
        RegisterPage(self.root)  



class RegisterPage:
    """the sign up interface"""

    def __init__(self, master=None):
        self.root = master
        self.root.title('Sign up')
        self.root.geometry('400x250')
        self.conn = sqlite3.connect('mydb.db')
        self.username = tk.StringVar()
        self.password0 = tk.StringVar()  
        self.password1 = tk.StringVar()
        self.page = tk.Frame(self.root)
        self.createpage()

    def createpage(self):
        """page lay out"""
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

    def repage(self):  
        """go back to the login page"""
        self.page.destroy()
        self.conn.close()
        LoginPage(self.root)

    def register(self):
        """register function"""
        if self.password0.get() != self.password1.get():  
            messagebox.showwarning('Error', 'The two passwords do not match')
        elif len(self.username.get()) == 0 or len(self.password0.get()) == 0:  
            messagebox.showerror("Error", "Input is null")
        else:
            curs = self.conn.cursor()
            query = 'insert into loginuser values (?,?,?,?)'  
            val = [self.username.get(), self.password0.get(), "student", -1]
            try:
                curs.execute(query, val)  
                self.conn.commit()
                self.conn.close()
                messagebox.showinfo("Success", "Register successfully, Press OK to return")
                self.page.destroy()
                LoginPage(self.root)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "This account is exist")  


class ScorePage(tk.Toplevel):
    """The page showing selected student's score"""

    def __init__(self, id):
        super().__init__()
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute('select name from studentUser where id = ?', (id, ))
        self.name = cur.fetchall()[0][0]
        cur.close()
        con.close()
        self.id = id
        self.clickedSubject = None  
        self.geometry("500x500")
        self.title(f"{self.name}'s score")
        self.dataTreeview = ttk.Treeview(self, show='headings', column=('subject', 'score'))
        self.subject = tk.StringVar()
        self.score = tk.StringVar()
        self.creatPage()

    def creatPage(self):
        tk.Label(self, text=f'Student ID: {self.id}').place(relx=0, rely=0, relwidth=0.4)
        tk.Label(self, text=f"Name: {self.name}").place(relx=0.5, rely=0, relwidth=0.4)
        tk.Label(self, text="subject:").place(relx=0.05, rely=0.1, relwidth=0.15)
        tk.Entry(self, textvariable=self.subject).place(relx=0.2, rely=0.1, relwidth=0.3)
        tk.Label(self, text="score:").place(relx=0.5, rely=0.1, relwidth=0.15)
        tk.Entry(self, textvariable=self.score).place(relx=0.65, rely=0.1, relwidth=0.3)
        tk.Button(self, text="Add", command=self.addScore).place(relx=0.1, rely=0.2, width=100)
        tk.Button(self, text="Delete", command=self.delScore).place(relx=0.4, rely=0.2, width=100)
        tk.Button(self, text="Modify", command=self.modifyScore).place(relx=0.7, rely=0.2, width=100)
        self.dataTreeview.place(rely=0.3, relwidth=0.97)
        self.dataTreeview.column('subject', width=100, anchor="center")
        self.dataTreeview.column('score', width=100, anchor="center")
        self.dataTreeview.heading('subject', text='Subject')
        self.dataTreeview.heading('score', text='Score')
        self.dataTreeview.bind('<ButtonRelease-1>',
        self.getClickedStudentNumber)
        self.showAllInfo()

    def getClickedStudentNumber(self, event):  
        self.clickedSubject = self.dataTreeview.item(
            self.dataTreeview.selection()[0], "values")[0]
        print("You click a subject: ", str(self.clickedSubject))

    def showAllInfo(self):
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item)  
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("select subject,score from scores where id = ?",(self.id, ))
        lst = cur.fetchall()
        print(lst)
        for item in lst:
            self.dataTreeview.insert("", 'end', text="line1", values=item)  
        cur.close()
        con.close()

    def addScore(self):
        """add a new score record"""
        if self.subject.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.score.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        else:
            list1 = [self.id, self.subject.get(), self.score.get()]
            con = sqlite3.connect("mydb.db")
            cur = con.cursor()
            cur.execute("insert into scores values(?,?,?)", tuple(list1))  
            con.commit()
            con.close()
            self.showAllInfo()

    def delScore(self):
        """delete a score record"""
        if self.clickedSubject == None:
            messagebox.showerror("Attention", "Delete failed, don\'t choose any record.")
            return
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("select * from scores where id = ?", (self.id, ))
        recordList = cur.fetchall()
        cur.close()
        con.close()
        flag = 0
        for i in range(len(recordList)):
            for item in recordList[i]:
                if self.clickedSubject == item:
                    flag = 1
                    con = sqlite3.connect("mydb.db")
                    cur = con.cursor()
                    cur.execute( "delete from scores where id = ? and subject = ?", (self.id, self.clickedSubject))  
                    con.commit()
                    cur.close()
                    con.close()
                    break
        if flag == 1:
            showinfo(title='Attention', message='Delete successfully')
            self.clickedSubject = None
        else:
            showerror(title='Attention', message='Delte failed')
        self.showAllInfo()

    def modifyScore(self):
        """modify ciliked record"""
        if self.clickedSubject == None:
            messagebox.showerror("Attention","Delete failed, don\'t choose any record.")
            return
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("select * from scores where id = ?", (self.id, ))
        recordList = cur.fetchall()
        cur.close()
        con.close()
        flag = 0
        for i in range(len(recordList)):
            for item in recordList[i]:
                if self.clickedSubject == item:
                    flag = 1
                    new_score = int(askstring("modify score", "The new score:"))
                    con = sqlite3.connect("mydb.db")
                    cur = con.cursor()
                    cur.execute( "update scores set score = ? where id = ? and subject = ?", (new_score, self.id, self.clickedSubject))
                    con.commit()
                    cur.close()
                    con.close()
                    break
        if flag == 1:
            showinfo(title='Attention', message='Modify successfully')
            self.clickedStudentNumber = None
        else:
            showerror(title='Attention', message='Modify failed')
        self.showAllInfo()


class MainUI_admin:
    """admin's control panel"""

    def __init__(self, master=None):
        self.root = master
        self.dbstr = "mydb.db"
        self.root.geometry('700x700+300+50')
        self.root.title('Student management system - admin')
        self.sid = tk.StringVar()  
        self.name = tk.StringVar()  
        self.sex = tk.StringVar()  
        self.age = tk.StringVar()  
        self.clickedStudentNumber = None  
        self.dataTreeview = ttk.Treeview(
        self.root,show='headings', column=('sid', 'name', 'sex', 'age', 'telephone','email'))  
        self.createPage()

    def logout(self):
        showinfo(" ", "Account is log out")
        self.root.destroy()

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
            self.dataTreeview.insert("", 'end', text="line1", values=item)  
        cur.close()
        con.close()

    def appendInfo(self):
        """Add student's information"""
        if self.sid.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.name.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.sex.get() == 0:
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.age.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        else:
            list1 = [self.sid.get(), self.name.get(), self.sex.get(), self.age.get(), '', '' ]  
            con = sqlite3.connect(self.dbstr)
            cur = con.cursor()
            cur.execute("insert into studentUser values(?,?,?,?,?,?)", tuple(list1))  
            con.commit()
            con.close()
            self.showAllInfo()

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
        if num == None:  
            showerror(title='Attention', message='Delete failed, don\'t choose any student')
            return
        for i in range(
                len(studentList)):  
            for item in studentList[i]:
                if int(num) == item:
                    flag = 1
                    con = sqlite3.connect(self.dbstr)
                    cur = con.cursor()
                    cur.execute("delete from studentUser where id = ?", (int(num), ))  
                    con.commit()
                    cur.close()
                    con.close()
                    break
        if flag == 1:
            showinfo(title='Attention', message='Delete successfully')
            self.clickedStudentNumber = None
        else:
            showerror(title='Attention', message='Delte failed')
        self.showAllInfo()

    def getClickedStudentNumber(self, event):  
        self.clickedStudentNumber = self.dataTreeview.item(
            self.dataTreeview.selection()[0], "values")[0]
        print("You click a student, his/her id is: ", str(self.clickedStudentNumber))

    def createPage(self):
        """Page layout"""
        self.sex = tk.StringVar()
        self.sex.set("Male")

        tk.Label(self.root,
                 text='Student Information Management System',
                 bg='white',
                 fg='blue',
                 font=('Times', 15)).pack(side=tk.TOP, fill='x')
        tk.Label(self.root, text="Student ID:").place(relx=0, rely=0.05, relwidth=0.1)
        tk.Entry(self.root, textvariable=self.sid).place(relx=0.1, rely=0.05, relwidth=0.37, height=25)
        tk.Label(self.root, text="Name:").place(relx=0.5, rely=0.05, relwidth=0.1)
        tk.Entry(self.root, textvariable=self.name).place(relx=0.6, rely=0.05, relwidth=0.37, height=25)
        tk.Label(self.root, text="Age:").place(relx=0, rely=0.1, relwidth=0.1)
        tk.Entry(self.root, textvariable=self.age).place(relx=0.1, rely=0.1, relwidth=0.15, height=25)
        tk.Radiobutton(self.root, text='Male', variable=self.sex, value="Male").place(relx=0.25, rely=0.1, relwidth=0.1)
        tk.Radiobutton(self.root, text='Female', variable=self.sex, value="Female").place(relx=0.35, rely=0.1, relwidth=0.1)
        tk.Button(self.root, text="Add", command=self.appendInfo).place(relx=0.5, rely=0.1, width=100)
        tk.Button(self.root, text="delete", command=self.deleteInfo).place(relx=0.65, rely=0.1, width=100)
        tk.Button(self.root, text="log out", command=self.logout).place(relx=0.8, rely=0.1, width=100)
        self.dataTreeview.column('sid', width=100, anchor="center")
        self.dataTreeview.column('name', width=100, anchor="center")
        self.dataTreeview.column('sex', width=100, anchor="center")
        self.dataTreeview.column('age', width=100, anchor="center")
        self.dataTreeview.column('telephone', width=100, anchor="center")
        self.dataTreeview.column('email', width=100, anchor="center")
        self.dataTreeview.heading('sid', text='ID')
        self.dataTreeview.heading('name', text='Name')
        self.dataTreeview.heading('sex', text='Gender')
        self.dataTreeview.heading('age', text='Age')
        self.dataTreeview.heading('telephone', text='Telephone')
        self.dataTreeview.heading('email', text='Email')
        self.dataTreeview.place(rely=0.2, relwidth=0.97)
        self.dataTreeview.bind('<ButtonRelease-1>',
        self.getClickedStudentNumber)
        self.showAllInfo()


class MainUI_teacher:
    """teacher's control panel"""

    def __init__(self, master=None):
        self.root = master
        self.dbstr = "mydb.db"
        self.root.geometry('700x700+300+50')
        self.root.title('Student management system - teacher')
        self.clickedStudentNumber = None  
        self.dataTreeview = ttk.Treeview(self.root, show='headings', column=('sid', 'name', 'sex', 'age', 'telephone','email'))  
        self.createPage()

    def logout(self):
        showinfo(" ", "Account is log out")
        self.root.destroy()

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
            self.dataTreeview.insert("", 'end', text="line1", values=item)
        cur.close()
        con.close()

    def showScore(self):
        "show selected student's score"
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
        if num == None:
            showerror(title='Attention', message='Failed, don\'t choose any student')
            return
        for i in range(len(studentList)):
            for item in studentList[i]:
                if int(num) == item:
                    flag = 1
                    ScorePage(int(num))  
                    self.clickedStudentNumber = None
                    break

    def getClickedStudentNumber(self, event):
        self.clickedStudentNumber = self.dataTreeview.item(
            self.dataTreeview.selection()[0], "values")[0]
        print("You click a student, his/her id is: ", str(self.clickedStudentNumber))
        self.showIDLabel.config(text=f"Choosed student's ID: {self.clickedStudentNumber}")

    def createPage(self):
        """Page layout"""
        tk.Label(self.root, text='Student Information Management System', bg='white', fg='blue', font=('Times', 15)).pack(side=tk.TOP, fill='x')
        self.showIDLabel = tk.Label(self.root, text=f"Choosed student's ID: {self.clickedStudentNumber}")
        self.showIDLabel.place(relx=0, rely=0.1, width=400)
        tk.Button(self.root, text="show score", command=self.showScore).place(relx=0.6, rely=0.1, width=100)
        tk.Button(self.root, text="log out", command=self.logout).place(relx=0.8, rely=0.1, width=100)
        self.dataTreeview.column('sid', width=100, anchor="center")
        self.dataTreeview.column('name', width=100, anchor="center")
        self.dataTreeview.column('sex', width=100, anchor="center")
        self.dataTreeview.column('age', width=100, anchor="center")
        self.dataTreeview.column('telephone', width=100, anchor="center")
        self.dataTreeview.column('email', width=100, anchor="center")
        self.dataTreeview.heading('sid', text='ID')
        self.dataTreeview.heading('name', text='Name')
        self.dataTreeview.heading('sex', text='Gender')
        self.dataTreeview.heading('age', text='Age')
        self.dataTreeview.heading('telephone', text='Telephone')
        self.dataTreeview.heading('email', text='Email')
        self.dataTreeview.place(rely=0.2, relwidth=0.97)
        self.dataTreeview.bind('<ButtonRelease-1>',
        self.getClickedStudentNumber)
        self.showAllInfo()


class MainUI_student:
    """student's control panel"""

    def __init__(self, id, master=None):
        self.root = master
        self.root.geometry('700x500+500+200')
        self.root.title('Student management system - student')
        self.id = int(id)
        self.showInfo()

    def logout(self):
        showinfo(" ", "Account is log out")
        self.root.destroy()

    def getInfo(self):
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("select * from studentUser where id=?", (self.id, ))
        self.name, self.sex, self.age, self.tel, self.email = cur.fetchall()[0][1:]
        cur.close()
        con.close()

    def displayScore(self):
        x = self.dataTreeview.get_children()
        for item in x:
            self.dataTreeview.delete(item)  
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()
        cur.execute("select subject,score from scores where id = ?", (self.id, ))
        lst = cur.fetchall()
        print(lst)
        for item in lst:
            self.dataTreeview.insert("", 'end', text="line1", values=item)  
        cur.close()
        con.close()

    def showInfo(self):
        """Page layout"""
        self.getInfo()
        self.page = tk.Frame(self.root)
        self.dataTreeview = ttk.Treeview(self.page, show='headings', column=('subject', 'score'))
        tk.Label(self.page, text='Student Information Management System', bg='white', fg='blue', font=('Times', 15)).grid(row=0, columnspan=3)
        tk.Label(self.page, text="Student ID: %s" % self.id).grid(row=1, column=0, padx=20, pady=20)
        tk.Label(self.page, text="Name: %s" % self.name).grid(row=1, column=1, padx=20, pady=20)
        tk.Label(self.page, text="Age: %s" % self.age).grid(row=1, column=2, padx=20, pady=20)
        tk.Label(self.page, text="Gender: %s" % self.sex).grid(row=2, column=0, padx=20, pady=20)
        tk.Label(self.page, text="Telephone: %s" % self.tel).grid(row=2, column=1, padx=20, pady=20)
        tk.Label(self.page, text="email: %s" % self.email).grid(row=2, column=2, padx=20, pady=20)
        tk.Button(self.page, text='modify', command=self.modify).grid(row=3, column=0, padx=20, pady=20)
        tk.Button(self.page, text="log out", command=self.logout).grid(row=3, column=1, padx=20, pady=20)
        self.dataTreeview.grid(row=4, columnspan=3, sticky=tk.E + tk.W)
        self.dataTreeview.column('subject', width=100, anchor="center")
        self.dataTreeview.column('score', width=100, anchor="center")
        self.dataTreeview.heading('subject', text='Subject')
        self.dataTreeview.heading('score', text='Score')
        self.displayScore()
        self.page.pack()

    def modify(self):
        self.page.destroy()
        self.page = tk.Frame(self.root)
        self.new_sex = tk.StringVar()
        self.new_age = tk.StringVar()
        self.new_tel = tk.StringVar()
        self.new_email = tk.StringVar()
        self.new_sex.set(self.sex)
        self.new_age.set(self.age)
        self.new_tel.set(self.tel)
        self.new_email.set(self.email)

        self.dataTreeview = ttk.Treeview(self.page, show='headings', column=('subject', 'score'))
        tk.Label(self.page, text='Student Information Management System', bg='white', fg='blue', font=('Times', 15)).grid(row=0, columnspan=4)
        tk.Label(self.page, text="Student ID: %s" % self.id).grid(row=1, column=0, padx=20, pady=20)
        tk.Label(self.page, text="Name: %s" % self.name).grid(row=1, column=1, padx=20, pady=20)
        tk.Label(self.page, text="Age:").grid(row=1, column=2, pady=20, sticky=tk.E)
        tk.Entry(self.page, textvariable=self.new_age).grid(row=1, column=3, pady=20)
        tk.Label(self.page, text="Telephone:").grid(row=2, column=0, pady=20)
        tk.Entry(self.page, textvariable=self.new_tel).grid(row=2, column=1, pady=20)
        tk.Label(self.page, text="Email:").grid(row=2, column=2, pady=20, sticky=tk.E)
        tk.Entry(self.page, textvariable=self.new_email).grid(row=2, column=3, pady=20)
        tk.Label(self.page, text="Gender:").grid(row=3, column=0, pady=20, sticky=tk.E)
        tk.OptionMenu(self.page, self.new_sex, 'Male', 'Female').grid(row=3, column=1, pady=20, sticky=tk.W)
        tk.Button(self.page, text='Save', command=self.commit).grid(row=3, column=2, padx=20, pady=20)
        tk.Button(self.page, text='undo', command=self.undo).grid(row=3, column=3, padx=20, pady=20)
        self.dataTreeview.grid(row=4, columnspan=4, sticky=tk.E + tk.W)
        self.dataTreeview.column('subject', width=100, anchor="center")
        self.dataTreeview.column('score', width=100, anchor="center")
        self.dataTreeview.heading('subject', text='Subject')
        self.dataTreeview.heading('score', text='Score')
        self.displayScore()
        self.page.pack()

    def commit(self):
        """commit the modify"""
        if self.new_age.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.new_email.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        elif self.new_tel.get() == "":
            showerror(title='Warning', message='The input couldn\'t be null')
        else:
            con = sqlite3.connect("mydb.db")
            cur = con.cursor()
            cur.execute("update studentUser set sex = ?, age = ?, tel = ?, email = ? where id = ?", (self.new_sex.get(), self.new_age.get(), self.new_tel.get(), self.new_email.get(), self.id))
            con.commit()
            cur.close()
            con.close()
            self.page.destroy()  
            self.showInfo()

    def undo(self):
        """undo the modify"""
        self.page.destroy()
        self.showInfo()


if __name__ == '__main__':
    if os.path.exists("mydb.db") is not True:  
        fp = open("mydb.db", "w")
        fp.close()
        con = sqlite3.connect("mydb.db")
        cur = con.cursor()   
        cur.execute('CREATE TABLE IF NOT EXISTS loginuser (username varchar(30) primary key, password varchar(30), type varchar(20),id int(10))')
        cur.execute('create table if not exists studentUser(id int(10) primary key,name varchar(20),sex char(2), age int(10), tel varchar(15), email varchar(20))')
        cur.execute('create table if not exists scores (id int(10), subject varchar(10), score int(10))')
        cur.execute("insert into loginuser values(?,?,?,?)", ['admin', 'admin', 'admin', -1])
        cur.execute("insert into loginuser values(?,?,?,?)", ['teacher', 'teacher', 'teacher', -1])
        con.commit()
        cur.close()
        con.close()
    root = tk.Tk()  
    LoginPage(root)  
    root.mainloop()  
    
