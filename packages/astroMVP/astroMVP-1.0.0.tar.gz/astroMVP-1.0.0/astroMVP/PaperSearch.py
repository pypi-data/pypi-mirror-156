#### Created 22 06 2022
## This file should be where all ADS functions are stored
import ads

class PaperSearch(object):
    """
    PaperSearch class encapsulates paper search queries and returns. 
    """

    def __init__(self, keyword, token):
        """__init__ a search for a paper

        Note:
            Must have an ads provided token to search

        Args:
            keyword (str): the searched for word or phrase.
            token (string): ads provided token for seraching

        """

        # saving input
        self.token = token
        self.keyword = keyword
        ads.config.token = self.token
        self.keywordSeach(self.keyword)

    def keywordSeach(self, keyword):
        """
        keywordsearch

        Searches for the keyword and returns the first paper that matched with the highest citation count
        
        Args:
            keyword (string): search term. The users desired inquiry

        Returns:
            paper (string): ads provided bibcode for the top result paper
        """
        self.keyword = keyword
        papers = list(ads.SearchQuery(q=keyword,  fl=['id', 'bibcode', 'title', 'citation_count', 'author', 'abstract', 'citation'])) #sort="citation_count"
        if len(papers) > 0:
            self.paper = papers[0].bibcode
        else:
            self.paper = None
        return self.paper

    def returnPaper(self):
        """
        returnPaper

        This function returns the search's paper title, author list, and abstract
        
        Args:
            keyword (string): search term. The users desired inquiry

        Returns:
            title (string): ads provided bibcode for the top result paper
            author (string): ads first author
            abstract (string): ads provided abstract
        """
        paper = list(ads.SearchQuery(bibcode=self.paper, fl=['title', 'first_author', 'abstract']))[0]
        return [paper.title, paper.first_author, paper.abstract]

    def returnCitation(self, n=5):
        """
        return citation

        This function returns the first n papers that cite the initial paper, ordered by citation count.

        Args: 
            n (int): number of articles to return. Default is 5

        Returns:
            list (list): n nested lists of citation articles information
                list[n, 0] (string): nth article's title
                list[n, 1] (string): nth article's first author
        """
        paper = list(ads.SearchQuery(bibcode=self.paper, fl=['title', 'first_author', 'abstract', 'citation']))[0]

        if not paper.citation:
            print("No citations for this article")
            return [None]*n

        cite_bibcodes=paper.citation
        cite_articles=[list(ads.SearchQuery(bibcode=bib, fl=['title','first_author', 'citation_count']))[0] for bib in cite_bibcodes]
        cite_sorted=sorted(cite_articles, key=lambda x: x.citation_count, reverse=True)
        cite_cut=cite_sorted[:n]
        return [[article.title, article.first_author] for article in cite_cut]

    def returnReference(self, n=5):
        """
        returns references

        This function returns the first n papers that cite the initial paper, ordered by citation count.

        Args: 
            n (int): number of articles to return. Default is 5

        Returns:
            list (list): n nested lists of citation articles information
                list[n, 0] (string): nth article's title
                list[n, 1] (string): nth article's first author

        """
        paper = list(ads.SearchQuery(bibcode=self.paper, fl=['title', 'author', 'abstract', 'reference']))[0]

        if not paper.reference:
            print("No reference for this article")
            return [None]*n

        ref_bibcodes=paper.reference[:n]
        ref_articles=[list(ads.SearchQuery(bibcode=bib, fl=['title','first_author', 'citation_count']))[0] for bib in ref_bibcodes]
        ref_sorted=sorted(ref_articles, key=lambda x: x.citation_count, reverse=True)
        ref_cut=ref_sorted[:n]
        return [[article.title, article.first_author] for article in ref_cut]
