import requests, json, pandas as pd, ast, getpass, xlrd
from xml.etree import ElementTree as ET

class Boparse():
    
    def auth(self, url, data, headers):
        r = requests.post(url, headers=headers, data=json.dumps(data))
        return r

    def logoff(self, saptoken, host1):
        tempheader = {"X-SAP-LogonToken":saptoken}
        url_logoff = 'https://'+host1+'/biprws/logoff'
        requests.post(url_logoff, headers=tempheader)
        return print("logoff done")


    
    def q_result(self, document_list, header, hostname):
        url_doc='https://'+hostname+'/biprws/raylight/v1/documents'
        url_data='https://'+hostname+'/biprws/raylight/v1/documents'

        result = []
        final_result = []
        for i in document_list:
            document_open = requests.get(url_doc+'/'+ i, headers=header)
            final_result.append(document_open.json())
            
            dataprovider_open = requests.get(url_data+'/'+ i+'/dataproviders', headers=header)
            res = []
            q = ast.literal_eval(dataprovider_open.text)
            for keys, value in q.items():
                if keys == 'dataproviders':
                    for p, q in value.items():
                        if p == 'dataprovider':
                            for i1 in q:
                                temp = i1['id']
                                final_result.append('ID: '+i1['id'])
                                final_result.append('Name: '+i1['name'])
                                final_result.append('DataSourceTyep: '+i1['dataSourceType'])
                                if i1['dataSourceType'] == 'fhsql':
                                    q11 = (requests.get('https://'+hostname+'/biprws/raylight/v1/documents/'+i+'/dataproviders/'+i1['id'],headers=headers1))
                                    temp_data2 = ast.literal_eval(q11.text)
                                    for g,h in temp_data2.items():
                                        if g == 'dataprovider':
                                            for m,n in h.items():
                                                if m == 'properties':
                                                    for o,p in n.items():
                                                        for z in p:
                                                            if z['@key'] == 'sql':
                                                                # print(z['$'])
                                                                res.append('SQL '+i1['id']+' : '+z['$'])
                                else:
                                    q1 = (requests.get('https://'+hostname+'/biprws/raylight/v1/documents/'+i+'/dataproviders/'+i1['id']+'/queryplan',headers=headers1))                                
                                    temp_data = ast.literal_eval(q1.text)
                                    for c,d in temp_data.items():
                                        if c == 'queryplan':
                                            for e, f in d.items():
                                                if e == 'statement':
                                                    t2 = f['$']
                                                    res.append('SQL '+i1['id']+' : '+t2)
                                                
                                                
                            final_result.append(res)            
            result.append(final_result)
            a = json.dumps(result, indent=2)
            
            with open('Sample.txt','w') as outfile:
               json.dump(result, outfile, indent=4)

        #return 'a'

    def get_rep(self, token, host, protocol='https', port='443', content_type='application/json'):
        base_url = protocol + '://'+host #+ ':' + port
        self.bip_url = base_url + '/biprws/v1'        
        
        self.headers = {
                       'Accept':content_type,
                       'Content-type': 'application/json',
                       'X-SAP-LogonToken': token
                       }
        
        resp = requests.get(self.bip_url + '/documents', headers=self.headers)  
        
        t2 = ast.literal_eval(resp.text)
        for q,r in t2.items():
            if q == 'last':
                for r1,r2 in r.items():
                    if r1 == '__deferred':
                        str1 = r2['uri'][55:57]
                        str1 = int(str1)
                        
        
        temp_counter = 1
        id = []
        while temp_counter <= str1:
            temp_counter1 = str(temp_counter) 
            
            id_extract = requests.get(self.bip_url+ '/documents?page='+temp_counter1, headers=self.headers)
            temp = ast.literal_eval(id_extract.text)
            for keys1, values1 in temp.items():
                if keys1 == 'entries':
                    new_val1 = values1
                    for no1 in new_val1:
                        if isinstance(new_val1, list) and len(no1)>1:
                            if no1['type'] == 'Webi' and no1['name'][0:10] != 'do_not_use':
                                (id.append(no1['id']))

            temp_counter +=1


        self.q_result(id, self.headers, host)

        if resp.status_code == 200:
            return resp
        else:
            raise Exception('Could not Retrive')

    



if __name__ == "__main__":
    pass

    
    Hostname = input('Enter the fqdn url: ')
    Username = input('Enter the Username that you want to use: ')
    password = getpass.getpass(prompt='Enter the password for the above username: ')


    url = 'https://'+Hostname+'/biprws/logon/long'
    
    data ={
        "password": password,
        "clientType": "",
        "auth": "secEnterprise",
        "userName": "Administrator"
    }

    headers = {"Accept":"application/json",
                "Content-Type":"application/json"}

    parser = Boparse()
    a = parser.auth(url, data, headers)
    t1 = a.headers
    t2 = t1.get('X-SAP-LogonToken')


    headers1 = {"Accept":"application/json",
                "Content-Type":"application/json",
                "X-SAP-LogonToken":t2}

    reports = parser.get_rep(t2, Hostname)

    parser.logoff(t2, Hostname)
    
