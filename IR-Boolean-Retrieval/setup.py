import os
from string import punctuation
from nltk.tokenize import word_tokenize
import contractions
from nltk.stem import PorterStemmer
import json

ps=PorterStemmer()
DATASET_DIR=os.path.join(os.getcwd(),'dataset/ShortStories/')
TOTAL_DOCS=50
DISK_READ=False


class BooleanRetrievalSystem:

    def __init__(self):
        global punctuation
        global DISK_READ
        punctuation+='“”’‘—'  #inorder to deal with punctuations of different unicode
        self.vocabulary=dict()  #for positional index
        self.inverted_index=dict()  #for inverted index
        self.stop_word=["a", "is", "the", "of", "all", "and", "to", "can", "be", "as", "once"
                        , "for", "at", "am", "are", "has", "have", "had", "up", "his", "her", "in", "on", "no", "we", "do"]                

        if os.path.exists((os.path.join(os.getcwd(),'inverted_index.json'))) and os.path.exists((os.path.join(os.getcwd(),'positional_index.json'))):
            DISK_READ=True

        if DISK_READ:
            with open('inverted_index.json','r') as json_file:
                self.inverted_index=json.load(json_file)
            with open('positional_index.json','r') as json_file_2:
                self.vocabulary=json.load(json_file_2)        

    def pre_process(self,document):
        document=document.lower()  #lowers the text
        document=contractions.fix(document)  #remove contractions 
        document=document.translate(str.maketrans('','',punctuation))  #remove punctuations from text
        tokenize_word_list=word_tokenize(document) # make tokenizers 
        stem_tokenize_word_list=[ ps.stem(word) for word in tokenize_word_list ] #creating this in order to take out positions 
        tokenize_word_list=[ word for word in tokenize_word_list if word not in self.stop_word ] #remove stop words
        tokenize_word_list=[ ps.stem(word) for word in tokenize_word_list ] #apply stemming 
        tokenize_word_list=list(dict.fromkeys(tokenize_word_list))   #remove duplicates
        return (tokenize_word_list,stem_tokenize_word_list)

    def calculate_all_occurance(self,stem_list,docId):
        index=0
        while index<len(stem_list):
            if stem_list[index] in self.vocabulary:
                word=stem_list[index]
                if docId not in self.vocabulary[word]:
                    self.vocabulary[word][docId]=list()
                self.vocabulary[word][docId].append(index)    
            index+=1

    def create_vocab(self,word_list,stem_list,docId):

        for word in word_list:
            if word not in self.vocabulary:
                self.vocabulary[word]=dict()
                self.inverted_index[word]=list()
            self.inverted_index[word].append(docId)
        self.calculate_all_occurance(stem_list,docId)        
        
    def process_txt(self):
        global TOTAL_DOCS
        for txt_file in os.listdir(DATASET_DIR):
            if txt_file.endswith('.txt'):
                doc_id=int(txt_file.split('.')[0])
                f=open(os.path.join(DATASET_DIR,txt_file),'r',encoding='utf-8')
                word_list,stem_list=self.pre_process(f.read())
                self.create_vocab(word_list,stem_list,doc_id)
        TOTAL_DOCS=len(os.listdir(DATASET_DIR))
        self.write_files()

    def intersect_list(self,list_1,list_2):
        intersect_list=list()
        index1,index2=(0,0)
        while index1<len(list_1) and index2<len(list_2):
            if list_1[index1]==list_2[index2]:
                intersect_list.append(list_1[index1])
                index1+=1
                index2+=1
            elif list_1[index1]<list_2[index2]:
                index1+=1
            else:
                index2+=1

        return intersect_list

    def binary_search(self,search_list,position_1,position_2):
        l,r=(0,len(search_list)-1)
        while l<=r:
            m=l +(r-l)//2
            if search_list[m]<=position_1 and search_list[m]>=position_2 :
                return True
            elif search_list[m]<position_2:
                l=m+1
            else:
                r=m-1
        return False                

    def process_proximity_query(self,user_query):
        query_words,proximity_ratio=user_query.split('/')
        word1,word2=query_words.split()
        word2=word2.replace(' ','')
        word1=ps.stem(word1)
        word2=ps.stem(word2)
        list_1,list_2=(None,None)
        try:
            list_1=list(model.vocabulary[word1].keys())
            list_2=list(model.vocabulary[word2].keys())
        except:
            list_1=list()
            list_2=list()


        list_1.sort()
        list_2.sort()
        intersect_list=model.intersect_list(list_1,list_2)
        proximity_query_final_list=list()

        for docId in intersect_list:
            intersect_list1=self.vocabulary[word1][docId]
            intersect_list2=self.vocabulary[word2][docId]
            

            if len(intersect_list1)>len(intersect_list2):
                temp_list=intersect_list1
                intersect_list1=intersect_list2
                intersect_list2=temp_list

            for position in intersect_list1:
                if self.binary_search(intersect_list2,position+(int(proximity_ratio)+1),position-(int(proximity_ratio)+1)):
                    proximity_query_final_list.append(docId)
                    break

        print(proximity_query_final_list)
        return proximity_query_final_list


    def not_of_list(self,list_1):
        list_2=[ num for num in range(1,TOTAL_DOCS+1) ]

        for num in list_1:
            list_2.remove(num)

        return list_2    

    def process_boolean_query(self,user_query):
        op=None  #for storing operator
        values=list()  #for storing each word in query 

        index=0
        not_count=0
        user_query=user_query.lower().split()

        while index<len(user_query):
            if user_query[index]=='not':
                while index<len(user_query) and user_query[index]=='not':
                    index+=1
                    not_count+=1

                if not_count%2!=0:
                    if index!=len(user_query):
                        word=ps.stem(user_query[index])
                        value=None
                        try:
                            value=self.not_of_list(self.inverted_index[word])
                        except:
                            value=self.not_of_list(list())
                        values.append(value)
                    else:
                        return []

                else:
                    if index!=len(user_query):
                        word=ps.stem(user_query[index])
                        value=None
                        try:
                            value=self.inverted_index[word]
                        except:
                            value=list()
                        values.append(value)
                    else:
                        return []    
                
                not_count=0

            elif user_query[index]=='and' or user_query[index]=='or':
                op=user_query[index]
            else:
                word=ps.stem(user_query[index])
                value=None
                try:
                    value=self.inverted_index[word]
                except:
                    value=list()
                values.append(value)

            if len(values)>1:
                if op=='and':
                    list_1=values.pop()
                    list_2=values.pop()
                    list_1.sort()
                    list_2.sort()
                    values.append(self.intersect_list(list_1,list_2))
                elif op=='or':
                    list_1=values.pop()
                    list_2=values.pop()
                    values.append(list(set(list_1) | set(list_2) ))
                op=None    

            index+=1

        if len(values)==0:
            return []
        return values.pop()


    def write_files(self):
        inverted_index_json=json.dumps(self.inverted_index)
        positional_index_json=json.dumps(self.vocabulary)
        with open('inverted_index.json','w') as inverted_json:
            inverted_json.write(inverted_index_json)
        with open('positional_index.json','w') as positional_json:
            positional_json.write(positional_index_json)
                                

model=None
if __name__=='__main__':
    model=BooleanRetrievalSystem()
    if not DISK_READ:
        print('Index not found creating it')
        model.process_txt()
    flag=True
    while flag:
        user_query=input('Enter your query: ')
        if user_query=='-1':
            flag=False
            continue
        if '/' in user_query:
            model.process_proximity_query(user_query)
        else:
            print(model.process_boolean_query(user_query))
else:
    model=BooleanRetrievalSystem()
    if not DISK_READ:
        print('Index not found creating it')
        model.process_txt()
        


        
    

