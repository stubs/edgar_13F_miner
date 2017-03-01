#!/usr/bin/env python
"""
Aaron D. Gonzalez 
Coding Challenge from Quovo
Write code in Python that parses fund holdings pulled from EDGAR, given a ticker or CIK. Parse and generate tab-delimited text from the xml.
"""
from bs4 import BeautifulSoup
import csv
import re
import requests
import string

class PageData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.func_dict = {
                "titleOfClass": self.func_class,
                "cusip": self.func_cusip,
                "value": self.func_value,
                "sshPrnamtType": self.func_amttype
                }

        #Regex search patterns to help parse out more difficult 13F formats
        self.class_pattern = re.compile("((sponsored|spon)\s*[a-z\s]*|com\s*[a-z\s]*|ord\s*[a-z\s]*|ltd\s*[a-z\s]*|cl\s*[a-z\s]*)", re.IGNORECASE) #this will likely grow to a longer pattern :(
        self.cusip_pattern = re.compile("[a-z0-9]{8}[0-9]{1}", re.IGNORECASE)
        self.currency_pattern= re.compile("\$")
        self.value_pattern = re.compile("\d{1,3}(?:[,]\d{3})*")
        self.amttype_pattern = re.compile("(sh|prn)", re.IGNORECASE)


        #Program starts
        self.url = self.build_url(self.ticker)
        self.data = self.get_page_data(self.url)
        self.bsdata = BeautifulSoup(self.data, 'lxml')
        self.tables = self.bsdata.findAll('table')
        self.links = self.link_crawler(self.tables[2])
        self.parse_links = self.parse_files(self.links)

        for link in self.parse_links:
            report_dict = {}
            asset_dict = {}
            list_of_dicts = []
            print '\n' + "parsing url: " + link
            raw_data = self.get_page_data(link)
            lines = raw_data.split('\n')
            lines_leng = len(lines)

            for line in lines:
                if "FILED AS OF DATE:" in line:
                    report_dict['Report_Date'] = str(line[-8:])

                key_list = ['nameOfIssuer', 'titleOfClass', 'cusip', 'value', 'sshPrnamt', 'sshPrnamtType']
                for i in key_list:
                    if  i + ">" in line:
                        asset_dict[i] = str(line[line.find('>') + 1 : line.find('</')])
                        if len(asset_dict) == 6:
                            list_of_dicts.append(asset_dict)
                            report_dict['holdings'] = list_of_dicts
                            asset_dict = {}
            #print report_dict

            if len(report_dict) < 2:
                start_lines = []
                end_lines = []
                headers = '' 

                for i in range(lines_leng):
                    if "<S>" in lines[i]:
                        start_lines.append(i + 1)
                        headers = lines[i - 2] #TODO: unfortunately not all files have their headers fixed 2 lines above
                    if "</TABLE>" in lines[i]:
                        end_lines.append(i)
                    if "</Table>" in lines[i]:
                        end_lines.append(i)

                if len(start_lines) == len(end_lines): #This accounts for multiple tables split across page breaks
                    for indx, v in enumerate(start_lines):
                        for i in lines[start_lines[indx] : end_lines[indx]]:
                            del_ind_list = []
                            new_i = i.split('  ')

                            for ind, item in enumerate(new_i):
                                new_i[ind] = new_i[ind].strip()
                                if len(item) == 0:
                                    del_ind_list.append(ind)
                            del_ind_list.reverse()

                            for i in del_ind_list: #cull each row of empty indexes
                                del new_i[i]
                            #print new_i[:7]

                            for key in self.func_dict: #apply regex functions to row list
                                for i, e, in enumerate(new_i[:7]):
                                    if i == 0:
                                        asset_dict['nameOfIssuer'] = e

                                    if key == 'value':
                                        val_list = list(self.parse_row(new_i, i, key))
                                        if val_list:
                                            #print val_list
                                            if 'value' in asset_dict and 'sshPrnamt' in asset_dict:
                                                pass
                                            else:
                                                if '1000)' in headers: #implement multiply by 1000 and format back to  xxx,xxx
                                                    val_list[0] = "{:,}".format((int(val_list[0].replace(",","")) * 1000))
                                                    asset_dict['value'] = val_list[0]
                                                    asset_dict['sshPrnamt'] = val_list[1]
                                                else:
                                                    asset_dict['value'] = val_list[0]
                                                    asset_dict['sshPrnamt'] = val_list[1]
                                    else:
                                        val = self.parse_row(new_i, i, key)
                                        if val <> '':
                                            asset_dict[key] = val

                                    if link == 'https://www.sec.gov/Archives/edgar/data/1166308/000122107312000014/0001221073-12-000014.txt':
                                        print asset_dict
                                        assert False
                                    if len(asset_dict) == 6:
                                        list_of_dicts.append(asset_dict)
                                        report_dict['holdings'] = list_of_dicts
                                        asset_dict = {}
                #print report_dict
            self.writeout(report_dict, self.ticker, link)

    def func_issuer(self, row, index):
        pass

    def func_class(self, row, index):
        fld = row[index]
        return self.matcher(self.class_pattern, fld)

    def func_cusip(self, row, index):
        fld = row[index]
        return self.matcher(self.cusip_pattern, fld)

    def func_currency(self, row, index):
        pass

    def func_value(self, row, index):
        row_len = len(row)
        if index + 1 < row_len:
            fld1 = row[index]
            fld2 = row[index + 1]
            return self.matcher(self.value_pattern, fld1, fld2)
        else:
            return ''

    def func_amttype(self, row, index):
        fld = row[index]
        return self.matcher(self.amttype_pattern, fld)

    def parse_row(self, row, index, key):
        ret_val = ''
        if key == 'value':
            return self.func_dict[key](row, index)
        else:
            ret_val = self.func_dict[key](row, index)
            return ret_val

    def matcher(self, pattern, field , field2 = None):
        """

        """
        if field2 is None:
            try:
                start = pattern.search(field).start()
                match = pattern.match(field[start:])
                if match is None:
                    return ""
                else:
                    return match.group(0)
            except AttributeError:
                return ""
        else:
            try:
                tot_field = field + " " + field2
                #print tot_field
                list_r = re.findall(pattern, tot_field)
                if len(list_r) < 2 or len(list_r) > 2:
                    return ""
                else:
                    return list_r[0], list_r[1]
            except AttributeError:
                return ""

    def build_url(self, ticker):
        """
        TODO: Right now the type filter for 13F is hardcoded into url string.
        Consider making program able to comb through all diff types and filter only needed.
        """
        url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK={0}&action=getcompany&type=13F".format(ticker)
        return url

    def get_page_data(self, url):
        page = requests.get(url)
        return page.text

    #def get_col_array(self, table_index, col_index):
    """
    MIGHT NOT BE NEEDED IF OK WITH HARDCODING TYPE=13F INTO URL FUNCTION
    KEEP COMMENTED UNTIL KNOW REQUIREMENTS
    """
    #    col_field = []
    #    for row in self.tables[table_index].findAll('tr'):
    #        row_data = row.findAll('td')
    #        if row_data:
    #            field_record = row_data[col_index].find(text=True)
    #            if field_record:
    #                col_field.append(field_record)
    #                #col_field.append(field_record.encode('ascii'))
    #    return col_field

    def link_crawler(self, table):
        links = []
        link_urls = table.select('a[id="documentsbutton"]')
        for link in link_urls:
            link = link.get('href')
            link = string.replace(link, '-index.htm', '.txt')
            links.append(link)
        return links

    def parse_files(self, file_list):
        parse_list = []
        for item in file_list:
            parse_url = 'https://www.sec.gov' + item
            parse_list.append(parse_url)
        return parse_list

    def writeout(self, form_dict, ticker, link):
        try:
            file_name = form_dict["Report_Date"] + "_" + ticker + "_holdings.csv"
            with open(file_name, 'w') as f:
            #with open(form_dict["Report_Date"] + "_" + ticker + "_holdings.csv", 'w') as f:
                print "Data written to: " + file_name
                writer = csv.writer(f, delimiter = "\t")
                col_headers = form_dict["holdings"][0].keys()
                #print col_headers
                writer.writerow(col_headers)
                #print col_headers
                for i in form_dict["holdings"]:
                    writer.writerow(i.values())
        except KeyError as e:
            file_name = link[-24:-4] + "_error_log.csv"
            with open(file_name, 'w') as f:
                writer = csv.writer(f, delimiter = "\t")
                print "Parsing error occurred with this url: " + link + "\n\n" + str(e)
                writer.writerow("Parsing error occurred with this url: " + link  + "\n\n" + str(e))


def main():
    import sys
    try:
        pass
        in_ticker = sys.argv[1]
    except:
        print('\nError\n')
        sys.exit(0)

    PageData(in_ticker)

if __name__ == "__main__":
    main()
