import tkinter
from setup import model

window=tkinter.Tk()
window.title('Boolean Retrieval System')
window.attributes('-fullscreen', True)
window.configure(bg='#ffffff')


query_input=tkinter.StringVar()
initial_content='1) Type in any boolean query of form eg: beard,not love,not god and love,not water and love or god\n2) Type in any proximity query of form eg: (smiling face/3),(filling room /1)\n3) Make Sure Boolean Query doesnot contain any brackets\n4) Proximity Query is assumed to be retrieved in any order\n5) Make sure format and spelling of words are correct.'

top_frame=tkinter.Frame(window,bg='#ffffff')
top_frame.pack(side='top')
input_frame=tkinter.Frame(window,bg='#ffffff')
input_frame.pack(side='left',anchor='nw')
result_frame=tkinter.Frame(window,bg='#ffffff')
result_frame.pack(side='right',anchor='ne')

tkinter.Label(top_frame,text='Boolean Retrieval System K18-1044',font=('Times New Roman',40),bg='dark green',fg='white',width=100).pack()
tkinter.Label(top_frame,text=initial_content,borderwidth=5,relief='sunken',fg='red',font=("Times", "11", "bold"),bg='#ffffff').pack(padx=20,pady=40,ipady=10,ipadx=5)

tkinter.Label(input_frame,text='Input Query',font=('Times New Roman',25,'bold'),bg='#ffffff',fg='green').pack()
query_entry=tkinter.Entry(input_frame,textvariable=query_input,bg='#ffffff',borderwidth=5,relief='sunken')
query_entry.pack(ipady=5,ipadx=200,padx=50)


tkinter.Label(result_frame,text='Result-set',font=('Times New Roman',25,'bold'),bg='#ffffff',fg='green').pack()
text_area = tkinter.Text(result_frame,height=5,font=('Times New Roman',14),bg='#ffffff',relief='sunken',borderwidth=4)
text_area.pack(side="left",padx=30)
scroll_bar=tkinter.Scrollbar(result_frame,orient="vertical",command=text_area.yview)
scroll_bar.pack(side="left",expand=True, fill="y",padx=10)
text_area.configure(yscrollcommand=scroll_bar.set)


def process_submit_query():
    text_area.delete('1.0',tkinter.END)
    user_query=query_entry.get()
    if user_query!='' and user_query!='Kindly type something!':
        result=None
        if '/' in user_query:
            result=model.process_proximity_query(user_query)
        else:
            result=model.process_boolean_query(user_query)

        doc_length=len(result)
        if doc_length==0:
            result='Query resulted in empty set..'
        else:
            result=[ str(num) for num in result ]
            result=','.join(result)

        result+='\nDocuments Received: {}'.format(doc_length)

        text_area.insert(tkinter.END,result)
        query_input.set('')
    else:
        query_input.set('Kindly type something!')    

def exit_code():
    quit()


tkinter.Button(input_frame,text='Submit',font=('Times New Roman',12,'bold','underline'),command=process_submit_query,borderwidth=6,bg='#ffffff',fg='green').pack(pady=10,ipadx=15,ipady=5)
tkinter.Button(input_frame,text='Exit',font=('Times New Roman',12,'bold','underline'),command=exit_code,borderwidth=6,bg='#ffffff',fg='red').pack(pady=10,ipadx=15,ipady=5)

window.mainloop()