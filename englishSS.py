import os
import spacy
import re
from spacy.lang.en import English

def wordSegmentation(fileName):
    with open(os.environ['HOME']+'/Documents/articles/'+fileName,'r+') as f:
        data1 = f.readlines()
        contentList = data1[3:]

        content = ''
        for i in contentList:
            content += re.sub('\n|\t','',i)
        #print(content)            

        sentences = ''
        # spacy with rule-based pipeline component
        nlp = English()
        sentencizer = nlp.create_pipe("sentencizer")
        nlp.add_pipe(sentencizer)
        doc = nlp(content)
        
        data1[3:] = ''
        for sent in doc.sents:
            data1.append(sent.text+'\n')
        #print(data1)
        
        f.seek(0)
        f.truncate()
        for i in data1:
            f.write(i)

if __name__ == '__main__':
     
    files = os.listdir(os.environ['HOME']+'/documents/articles')

    num = 0
    for f in files:
        if re.search('en.txt',f) and not re.search('_TW_',f):
            print(f)
            wordSegmentation(f)
    
            

    

