import tkinter as tk
from tkinter import ttk
from tkinter.font import BOLD
from tkinter.tix import DisplayStyle
import webbrowser
import requests 
import validators
from PIL import ImageTk, Image

#Diplsay Input
def input():
    """
    Interactive box for Input Values

    Returns:
        the values that the user typed in the box:
        token_input (string): the users ads token
        keyword_input (string): the keyword the user gave
    """


    # root window
    root = tk.Tk()
    root.resizable(False, False)
    root.title('Astro MVP')
    root.geometry("500x250")

    #Add header image!
    frame = tk.Frame(root, width=600, height=400)
    frame.pack()
    frame.place(anchor='center', relx=0.5, rely=0.5)
    img = ImageTk.PhotoImage(Image.open("astromvplogo.png"))
    label = tk.Label(root, image = img)
    label.pack()



    # store keyword address and pub_year
    keyword = tk.StringVar()
    ads = tk.StringVar()

    # submit frame
    submit_frame = ttk.Frame(root)
    submit_frame.pack(padx=10, pady=10, fill='x', expand=True,side=tk.BOTTOM)

    #little intro:
    introtext = 'Welcome to Astro MVP. We use the Astrophysics Data System to \nfind the most valuable astronomy paper related to your keyword.\n  '
    intro_label = ttk.Label(submit_frame, text=introtext,font = ('Helvetica', 14))
    intro_label.pack(fill='none',expand=False) 


    # keywords
    keyword_label = ttk.Label(submit_frame, text="Keyword:",font = ('Helvetica', 14))
    keyword_label.pack(fill='x', expand=True)

    keyword_entry = ttk.Entry(submit_frame, textvariable=keyword)
    keyword_entry.pack(fill='x', expand=True)
    keyword_entry.focus()


    #THIS IS WHERE YOU GRAB THE VAlUES SUMBMITTED IN THE TEXTBOX
    keyword_input = []
    def submit_clicked():
        keyword_input.append(keyword.get())
        root.destroy()
        return keyword_input



    submit_button = ttk.Button(submit_frame, text="Submit", command=submit_clicked)
    submit_button.pack(fill='x', expand=True, pady=10)

    root.mainloop()


#Test Input Display 
# input()

#OUTPUT DISPLAY

def output(title,authors,abstract,urls): 

    """
    Displays the output (title,author,abstract) from papersearch.py in box

    """

    root = tk.Tk()
    root.title('Astro MVP')
    #Add header image!
    frame = tk.Frame(root) 
    frame.pack()
    frame.place(anchor='n', relx=0.0, rely=0.0)
    img = ImageTk.PhotoImage(Image.open("astromvplogo.png"))
    label = tk.Label(root, image = img)
    label.pack()

    S = tk.Scrollbar(root)
    T = tk.Text(root, height=35, width=40,font = ('Helvetica', 18),bd=0)
    S.pack(side=tk.TOP)
    T.pack(side=tk.TOP,fill='both',expand=True) 
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)

  
    def uri_exists(url_value):
        for i in url_value: 
            valid=validators.url(i) 
            if valid==True:
                url_value = i 
            else:
                url_value = 'https://ui.adsabs.harvard.edu/'

        return url_value

    the_url = uri_exists(urls)


    # title_quote = 'TITLE: \n'
    # author_quote = 'FIRST AUTHOR: \n'
    # abstract_quote = 'ABSTRACT: \n' 
    

    quote = 'TITLE\n'+ title[0] + '\n \n' + 'FIRST AUTHOR: \n' + authors + '\n \n'  + 'ABSTRACT: \n' + abstract 

    T.insert(tk.END, quote) 

    def gotolink():
        webbrowser.open(the_url,new=1)

    def searchagain():
        root.destroy()
        import main


    submit_button = tk.Button(root, text="Go To Paper", pady=0, command=gotolink,bg='white',activebackground='white',fg='black',font = ('Helvetica', 18),activeforeground='white',bd=0)
    submit_button.pack(side=tk.TOP,fill='both',expand=True)

    submit_button = tk.Button(root, text="Search Again", pady=0, command=searchagain,bg='white',activebackground='white',fg='black',font = ('Helvetica', 18),activeforeground='white',bd=0)
    submit_button.pack(side=tk.TOP,fill='both',expand=True)

    tk.mainloop()


#Test Output 
# title = ['example title goes here.'] 
# authors = 'E. Komatsu(Texas U.)'
# abstract = '(Abridged) The WMAP 5-year data strongly limit deviations from the minimal LCDM model. We constrain the physics of inflation via Gaussianity, adiabaticity, the power spectrum shape, gravitational waves, and spatial curvature. We also constrain the properties of dark energy, parity-violation, and neutrinos. We detect no convincing deviations from the minimal model. The parameters of the LCDM model, derived from WMAP combined with the distance measurements from the Type Ia supernovae (SN) and the Baryon Acoustic Oscillations (BAO), are: Omega_b=0.0462+-0.0015, Omega_c=0.233+-0.013, Omega_Lambda=0.721+-0.015, H_0=70.1+-1.3 km/s/Mpc, n_s=0.960+0.014-0.013, tau=0.084+-0.016, and sigma_8=0.817+-0.026. With WMAP+BAO+SN, we find the tensor-to-scalar ratio r<0.20 (95% CL), and n_s>1 is disfavored regardless of r. We obtain tight, simultaneous limits on the (constant) equation of state of dark energy and curvature. We provide a set of...' 
# urls =  ['http://$SIMBAD$/simbo.pl?bibcode=2009ApJS..180..330K','http://iopscience.iop.org/article/10.1088/0067-0049/180/2/330/pdf','http://inspirehep.net/search?p=find+eprint+arXiv:0803.0547']

# output(title,authors,abstract,urls)