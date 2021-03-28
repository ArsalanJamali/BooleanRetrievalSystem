import os
from string import punctuation
from nltk.tokenize import word_tokenize
import contractions
from nltk.stem import PorterStemmer

ps=PorterStemmer()
DATASET_DIR=os.path.join(os.getcwd(),'dataset/ShortStories/')


class BooleanRetrievalSystem:

    def __init__(self):
        global punctuation
        punctuation+='“”’‘—'
        self.vocabulary=dict()
        self.stop_word=["a", "is", "the", "of", "all", "and", "to", "can", "be", "as", "once"
                        , "for", "at", "am", "are", "has", "have", "had", "up", "his", "her", "in", "on", "no", "we", "do"]                

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
        self.calculate_all_occurance(stem_list,docId)        
        
    def process_txt(self):
        for txt_file in os.listdir(DATASET_DIR):
            if txt_file.endswith('.txt'):
                doc_id=int(txt_file.split('.')[0])
                f=open(os.path.join(DATASET_DIR,txt_file),'r',encoding='utf-8')
                word_list,stem_list=self.pre_process(f.read())
                self.create_vocab(word_list,stem_list,doc_id)
        #print(self.vocabulary)    

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

    def binary_search(self,search_list,num_to_search):
        l,r=(0,len(search_list)-1)
        while l<=r:
            m=l +(r-l)//2
            if search_list[m]==num_to_search:
                return True
            elif search_list[m]<num_to_search:
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
        list_1=list(model.vocabulary[word1].keys())
        list_2=list(model.vocabulary[word2].keys())
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
                if self.binary_search(intersect_list2,position+(int(proximity_ratio)+1)):
                    proximity_query_final_list.append(docId)
                    break

        print(proximity_query_final_list)        


if __name__=='__main__':
    model=BooleanRetrievalSystem()
    model.process_txt()
    user_query=input('Enter your query: ')
    if '/' in user_query:
        model.process_proximity_query(user_query)

        
    




        


