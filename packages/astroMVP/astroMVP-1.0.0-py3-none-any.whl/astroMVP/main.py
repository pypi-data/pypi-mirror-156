# Created 22 06 2022
# Here we will write the run? files

import display 

keyword_input,token_input = display.input()
print(token_input)
import PaperSearch as ps

search1 = ps.PaperSearch(keyword_input[0], token_input[0])
if search1.paper:
    print("bibcode:", search1.paper)
    paper_info = search1.returnPaper()
    print("Paper Returned:", paper_info)
    title = paper_info[0]
    authors= paper_info[1]
    abstract = paper_info[2]  

else: 
    print("No papers found")
    title = 'no title found for ' + keyword_input
    authors= 'NA'
    abstract = 'NA'


display.output(title,authors,abstract) 
