from __future__ import print_function
from bs4 import BeautifulSoup
import urllib2
import logging

class data_saver(object):
    """ Class for saving values extracted from university's page
        In this realization a text file with tab separation is used in the 'save_param' function
    """ 
    def __init__(self, univ_num,fl=None):
        """ univ_num - id of university at monitoring site, first value at string in the output file
            fl - descriptor of the output file
        """
        self.univ_num = univ_num
        self.fl = fl            
        
    def __str__(self):
        return "num - %s" %self.univ_num
    
   
    def save_param(self,name,val):
        print ("%s\t%s\t%s" % (self.univ_num,name,val),file=self.fl)
    
    def close(self):
        self.fl.close()

class monitoring_site(object):
    """ The wrapper for site's url 
        get_page returns wrapper for the specific university page to parse
    """
    def __init__(self,url_template):
        self.url_template = url_template
        
    def __str__(self):
        return 'url - %' % self.url_template
    
    def get_page(self,univ_num):
        """ univ_num - id of university
        """
        return university_page(univ_num,self.url_template % univ_num)
    
class university_page(object):
    """ The wrapper for university's page, such as http://indicators.miccedu.ru/monitoring/inst.php?id=1719         
    """
    def __init__(self,univ_num,url):        
        self.univ_num = univ_num
        self.url = url
        self.page = urllib2.urlopen(url)
        self.soup = BeautifulSoup(self.page)
        self.name = self.exists()
    
    def __str__(self):
        return 'url - %s, name - %s ' % (self.url,self.name)

    def __nonzero__(self):
        """ Used for 'if not page is None:'
        """    
        return not self.name is None
    
    def get_saver(self,fl):
        """ Returns saver with setted id of current university
        """
        return data_saver(self.univ_num,fl)

    def exists(self):
        """ Checks information existence in the current page and returns name of the university
        """
        table = self.soup.find("table", { "id" : "info" })
        if table is None:
            return None
        else:
            return table.findAll("tr")[0].findAll("td")[1].find(text=True).encode('utf-8')
        
    def parse_head(self,saver):
        """ Parses name, region and coordinates of the university and saves by the saver 
        """
        table = self.soup.find("table", { "id" : "info" })
        if table is None:
            return
        rows = table.findAll("tr")
        cells = rows[0].findAll("td")
        univ_name = cells[1].find(text=True).encode('utf-8')
        cells = rows[1].findAll("td")
        univ_region = cells[1].find(text=True).encode('utf-8')
        univ_coord = self.soup.find("span",{"id" : "post"})["coordinates"]
        
        saver.save_param("name",univ_name)
        saver.save_param("region",univ_region)
        saver.save_param("coord",univ_coord)
    
    def parse_base_results(self,saver):
        """ Parses main values of effectiveness  
        """
        table = self.soup.find("table", { "id" : "result" })
        if table is None:
            return
        i=0
        for row in table.findAll("tr"):
            cells = row.findAll("td")
            indi_num = cells[0].find(text=True).encode('utf-8')
            indi_name = cells[1].find(text=True).encode('utf-8')
            indi_value = cells[2].find(text=True).encode('utf-8')
            indi_tresh = cells[3].find(text=True).encode('utf-8')
            indi_diff = cells[4].find(text=True).encode('utf-8')
            if i >0:
                saver.save_param(indi_num,indi_value)
            i=i+1
    
    def parse_all_results(self,saver):
        """ Parses all values of effectiveness  
        """
        tables = self.soup.findAll("table", { "class" : "napde" })
        if tables is None:
            return
        for table in tables:
            i = 0
            for row in table.findAll("tr"):
                cells = row.findAll("td")
                indi_num = cells[0].find(text=True).encode('utf-8')
                indi_name = cells[1].find(text=True).encode('utf-8')
                indi_meter = cells[2].find(text=True).encode('utf-8')    
                indi_value = cells[3].find(text=True).encode('utf-8')        
                if i>0:
                    saver.save_param(indi_num,indi_value)
                i=i+1
    
    def parse_by_ugs(self,saver):
        """ Parses all values of effectiveness  
        """
        table = self.soup.find("table", { "id" : "analis_reg" })
        indi_name = ''
        indi_value = ''
        if table is None:
            return
        i = 0
        for row in table.findAll("tr"):
                cells = row.findAll("td")
                j = 0
                indi_name = ''
                indi_value = ''
                for cell in cells:
                    r = cell.find(text=True).encode('utf-8') if not cell.find(text=True) is None else ''
                    if j == 0:
                        indi_name = r
                    if j == 1:
                        indi_value = r
                    j = j+1    
                if i>0 and indi_name.find(' - ')>0:
                   saver.save_param(indi_name,indi_value)
                i=i+1
    

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG,format = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
    with open("params1.txt","w+") as fl1, open("ugs1.txt","w+") as fl2:

        ms = monitoring_site("http://indicators.miccedu.ru/monitoring/inst.php?id=%s")
        for i in range(10):
            pg = ms.get_page(i)
            logging.debug("university %s was opened" % i)
            if pg: 
                pg.parse_head(pg.get_saver(fl1))
                pg.parse_base_results(pg.get_saver(fl1))
                pg.parse_all_results(pg.get_saver(fl1))
                pg.parse_by_ugs(pg.get_saver(fl2))
