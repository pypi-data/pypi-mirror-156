
#ads token limk https://ui.adsabs.harvard.edu/user/settings/token
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

#INPUT DISPLAY

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
    root.geometry("300x170")
    root.resizable(False, False)
    root.title('Astro MVP')

    # store keyword address and pub_year
    keyword = tk.StringVar()
    ads = tk.StringVar()

    # submit frame
    submit_frame = ttk.Frame(root)
    submit_frame.pack(padx=10, pady=10, fill='x', expand=True)

    #ADS 
    ADS_label = ttk.Label(submit_frame, text="ADS Token:")
    ADS_label.pack(fill='x', expand=True)

    ADS_entry = ttk.Entry(submit_frame, textvariable=ads)
    ADS_entry.pack(fill='x', expand=True)
    ADS_entry.focus()

    # keywords
    keyword_label = ttk.Label(submit_frame, text="Keyword(s):")
    keyword_label.pack(fill='x', expand=True)

    keyword_entry = ttk.Entry(submit_frame, textvariable=keyword)
    keyword_entry.pack(fill='x', expand=True)
    keyword_entry.focus()

    #To add a search option for the publication year 
    # pub_year
    # pub_year_label = ttk.Label(submit_frame, text="Publication Year:")
    # pub_year_label.pack(fill='x', expand=True)

    # pub_year_entry = ttk.Entry(submit_frame, textvariable=pub_year, show="*")
    # pub_year_entry.pack(fill='x', expand=True)


    #THIS IS WHERE YOU GRAB THE VAlUES SUMBMITTED IN THE TEXTBOX
    keyword_input,token_input = [],[]
    def submit_clicked():
        keyword_input.append(keyword.get())
        token_input.append(ads.get())
        root.destroy()
        return keyword_input,token_input 



    submit_button = ttk.Button(submit_frame, text="Submit", command=submit_clicked)
    submit_button.pack(fill='x', expand=True, pady=10)

    root.mainloop()

    return keyword_input,token_input 


#OUTPUT DISPLAY

def output(title,authors,abstract): 

    """
    Displays the output (title,author,abstract) from papersearch.py in box

    """

    output = 'TITLE:'+ title[0] + '\n \n' + 'AUTHORS: ' + authors + '\n \n'  + 'ABSTRACT: ' + abstract

    root = tk.Tk()
    root.title('Astro MVP')
    S = tk.Scrollbar(root)
    T = tk.Text(root, height=30, width=100)
    S.pack(side=tk.RIGHT, fill=tk.Y)
    T.pack(side=tk.LEFT, fill=tk.Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)
    quote = output
    T.insert(tk.END, quote)

    tk.mainloop()



#EXAMPLE WITH PRETEND DATA 

# title = 'The article title'
# authors ='the authors'
# abstract = 'Porttitor leo a diam sollicitudin tempor. Arcu dui vivamus arcu felis. Augue interdum velit euismod in. Sit amet nulla facilisi morbi tempus iaculis urna. Turpis massa sed elementum tempus egestas sed. Sit amet aliquam id diam maecenas ultricies mi. Nunc mattis enim ut tellus elementum sagittis vitae et. Sit amet massa vitae tortor condimentum lacinia quis. In fermentum posuere urna nec. Ut consequat semper viverra nam libero justo laoreet sit. Consequat semper viverra nam libero justo laoreet. Sagittis eu volutpat odio facilisis mauris. Erat nam at lectus urna duis convallis convallis tellus id. Magna etiam tempor orci eu lobortis elementum nibh. Etiam sit amet nisl purus.'
# output(title,authors,abstract) 



### SOME OTHER STUFF TO PLAY WITH LATER: 
# def frame_sentence():
#     title = paper_info[0][0]
#     authors = paper_info[1][0]
#     abstract = paper_info[2][0]

#     disp_tf.insert(0,f'{title} // {authors} // {abstract}.')

# ws = Tk()
# ws.title('Astro MVP')
# ws.geometry('400x500')
# ws.config(bg='#0f4b6e')

# name_tf = Entry(ws)
# age_tf = Entry(ws)
# descipline_tf = Entry(ws)

# name_lbl = Label(
#     ws,
#     text='Name',
#     bg='#0f4b6e',
#     fg='white'
# )
# age_lbl = Label(
#     ws,
#     text='Age',
#     bg='#0f4b6e',
#     fg='white'
# )

# descipline_lbl = Label(
#     ws,
#     text='Descipline',
#     bg='#0f4b6e',
#     fg='white'
# )

# name_lbl.pack()
# name_tf.pack()
# age_lbl.pack()
# age_tf.pack()
# descipline_lbl.pack()
# descipline_tf.pack()

# btn = Button(
#     ws,
#     text='Submit',
#     relief=SOLID,
#     command=frame_sentence
# )
# btn.pack(pady=10)

# disp_tf = Entry(
#     ws, 
#     width=38,
#     font=('Arial', 14)
#     )


# disp_tf.pack(pady=20)


# ws.mainloop()