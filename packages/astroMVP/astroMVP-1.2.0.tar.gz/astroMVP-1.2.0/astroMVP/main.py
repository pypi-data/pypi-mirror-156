# Created 22 06 2022
# Here we will write the run? files

import display 
import PaperSearch as ps

#input
keyword_input = display.input()

#paper search
search1 = ps.PaperSearch(str(keyword_input)) 
if search1.paper:
    print("bibcode:", search1.paper)
    paper_info = search1.returnPaper()
    print("Paper Returned:", paper_info)
    title = paper_info[0]
    authors= paper_info[1]
    abstract = paper_info[2]  
    urls = paper_info[3]  

else: 
    print("No papers found")
    title = 'no title found for ' + keyword_input
    authors= 'NA'
    abstract = 'NA'
    urls = 'NA'

#display output
display.output(title,authors,abstract,urls) 
