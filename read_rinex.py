
infile = "database/rinex/2014/alar0011.14o"

def get_header(infile):

    lines = open(infile, "r").readlines()
    
    header = []
    
    for line in lines:
        
        if "END OF HEADER" in line:
            break
        else:
            header.append(line.strip())
            
    return header 

def attributes(header):
    
    dict_infos = {}
    
    for num in range(len(header)):
        elements = header[num].split("    ")
        
        info_type = elements[-1].replace(" ", "")
        
        info_obj = [i for i in elements[:-1] if i != ""]
    
        dict_infos[info_type] = info_obj
    
    
    return dict_infos

lines = open(infile, "r").readlines()

#start_data = lines.find("END OF HEADER")


#outline = lines[start_data:].strip()

        
current = lines[15:33]


print(current[0])

