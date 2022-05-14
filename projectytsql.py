from tkinter import *
from tkinter import messagebox as ms
import sqlite3
import os
from pytube import YouTube
import re,urllib.parse, urllib.request
import json
import subprocess



lastid = 0




with sqlite3.connect('data/database.db') as db:
    c = db.cursor()

c.execute('CREATE TABLE IF NOT EXISTS songs(id INT ,username TEXT NOT NULL,song TEXT);')
c.execute('CREATE TABLE IF NOT EXISTS user ( id INT PRIMARY KEY, username TEXT NOT NULL,password TEXT NOT NULL);')
db.commit()
db.close()




class app:
    def __init__(self, master):
        self.master = master
        self.username = StringVar()
        self.password = StringVar()
        self.n_username = StringVar()
        self.n_password = StringVar()
        self.song= StringVar()
        self.frames()
        self.user= StringVar()
        self.id= 0
        self.listbox= None

    # Login Function
    def login(self):
        with sqlite3.connect('data/database.db') as db:
            c = db.cursor()

        find_user = ('SELECT * FROM user WHERE username = ? and password = ?')
        c.execute(find_user, [(self.username.get()), (self.password.get())])
        result = c.fetchall()
        c.execute('SELECT id FROM user WHERE username = ?', [(self.username.get())])
        self.id = c.fetchall()
        for row in self.id:
            self.id = row[0]
        if result:
            self.user= self.username.get()
            self.log.pack_forget()
            self.songframe()
        else:
            ms.showerror('Error','Username Not Found.')


    def songframe(self):
        with sqlite3.connect('data/database.db') as db:
            c = db.cursor()
        self.head['text'] = 'Download Songs'
        self.head['pady'] = 10
        self.song_frame = Frame(self.master, bg='#00ff00')
        Label(self.song_frame, text='Enter Song to download', font=('IMPACT', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.song_frame, textvariable=self.song, bd=5, font=('', 15)).grid(row=0, column=1)
        Button(self.song_frame, text='Download', command=self.play).grid(row=0, column=2)
        Label(self.song_frame, text='Songs You have Downloaded:', font=('freestyle script regular', 20), pady=5, padx=5).grid(row=1, column=0)
        Button(self.song_frame, text='Open folder', command=self.open).grid(row=1, column=2)
        self.listbox = Listbox(self.song_frame, height=30, width=70, font=('', 15))
        self.listbox.grid(row=3, column=0, columnspan=3)

        c.execute('SELECT song FROM songs WHERE username = ?', (self.user,))
        songs = c.fetchall()
        db.commit()
        self.song_frame.pack()
        for item in songs:
            self.listbox.insert(END, item[0])

    def open(self):
        #os.startfile('temp/{}'.format(self.user))
        subprocess.Popen(r'explorer /select,"./temp/{}/"'.format(self.user))

    def play(self):
        with sqlite3.connect('data/database.db') as db:
            c = db.cursor()
        query_string = urllib.parse.urlencode({"search_query": self.song.get()})
        formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
        clip2 = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])
        yt= YouTube(clip2)
        destination='./temp/{}/'.format(self.user)
        try:
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path=destination)

            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            ms.showinfo('Success', 'Song Downloaded')
            c.execute('INSERT INTO songs (id,username,song) VALUES (?,?,?)', (self.id,self.user, video.title))
            db.commit()
            self.listbox.insert(END, video.title)

        except Exception as e:
            print(e)
            ms.showerror('Song download failed')
            pass



    def new_user(self):
        # Connection
        with sqlite3.connect('data/database.db') as db:
            c = db.cursor()

        with open('data/config.json', 'r') as f:
            k = json.load(f)
            lastid=k['lastid']

        find_user = ('SELECT username FROM user WHERE username = ?')
        c.execute(find_user, [(self.n_username.get())])
        if c.fetchall():
            ms.showerror('Error!', 'Username Taken Try a Diffrent One.')
        else:
            ms.showinfo('Success!', 'Account Created!')
            self.loga()
        # Create New Account
        insert = 'INSERT INTO user(id,username,password) VALUES(?,?,?)'
        c.execute(insert, [(lastid),(self.n_username.get()), (self.n_password.get())])
        db.commit()
        with open('data/config.json', 'w') as n:
            y={"lastid":lastid+1}
            json.dump(y, n)



    def loga(self):
        self.username.set('')
        self.password.set('')
        self.crf.pack_forget()
        self.head['text'] = 'LOGIN'
        self.log.pack()



    def back(self):
        self.crf.pack_forget()
        self.frames()





    def cr(self):
        self.n_username.set('')
        self.n_password.set('')
        self.log.pack_forget()
        self.head['text'] = 'Create Account'
        self.crf.pack()

    def frames(self):
        self.head = Label(self.master, text='LOGIN', font=('IMPACT', 35), pady=10)
        self.head.pack()
        self.log = Frame(self.master, padx=10, pady=10)
        Label(self.log, text='Username: ', font=('', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.log, textvariable=self.username, bd=5, font=('', 15)).grid(row=0, column=1)
        Label(self.log, text='Password: ', font=('', 20), pady=5, padx=5).grid(sticky=W)

        Entry(self.log, textvariable=self.password, bd=5, font=('', 15), show='*').grid(row=1, column=1)
        Button(self.log, text=' Login ', bd=3, font=('', 15), padx=10, pady=10, command=self.login).grid()
        Button(self.log, text=' Create Account ', bd=3, font=('', 15), padx=10, pady=10, command=self.cr).grid(row=2,
                                                                                                              column=1)
        Label(self.log, text='21MIS1053 Haswanth Raj A', font=('', 20), pady=5, padx=5).grid(sticky=W)
        self.log.pack()


        self.crf = Frame(self.master, padx=10, pady=10)
        Label(self.crf, text='Username: ', font=('', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.crf, textvariable=self.n_username, bd=5, font=('', 15)).grid(row=0, column=1)
        Label(self.crf, text='Password: ', font=('', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.crf, textvariable=self.n_password, bd=5, font=('', 15), show='*').grid(row=1, column=1)
        Button(self.crf, text='Create Account', bd=3, font=('', 15), padx=5, pady=5, command=self.new_user).grid()
        Button(self.crf, text='Go to Login', bd=3, font=('', 15), padx=5, pady=5, command=self.back).grid(row=2,
                                                                                                         column=1)


if __name__ == '__main__':
    root = Tk()
    root.title('Login Form')
    root.geometry('950x600')
    root.config(background='#495252')
    app(root)
    root.mainloop()