# csv 
# sqlite3 user data
def readcsv():
    import csv

    with open('SmallWineDataset.csv', newline='') as winecsv:
        #reader = csv.reader(winecsv, delimiter="", quotechar='|') #other function
        reader = csv.DictReader(winecsv) #dictionary object could be passed to sqlite?
        headers = list(reader)
        #for row in headers:
            #print(row)
    return reader,headers

def givenType(headers,search):
    results = [row for row in headers if search in row["Type"]]
    return results

def query_data(rows, column, value,shortened=False): #general search function
    '''
    # Example usage
filtered = query_data(rows, "Type", "White")

for row in filtered:
    print(row)
    '''
    if shortened == False:
        search =  [row for row in rows if value in row[column]]
    else:
        search = [row[shortened] for row in rows if value in row[column]]
    ###terminal debug
    for row in search:
        print(row)
    ##################
    return search
def filter_view(headers,filters): #redo to copy and edit dictionary directly
    for filter in filters:
        search = [row[filter] for row in headers]
    ###terminal debug
    for row in search:
        print(row)



#################### Example uses ##################################

reader,headers=readcsv()

results = givenType(headers,"Red")
print(results)

query_data(headers,"Type","White",'Title')
filter_view(headers,['Title','Type'])