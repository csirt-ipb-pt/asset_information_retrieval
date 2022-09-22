import os
import sys
import csv

# Dictionary composed of the various fields of the asset tables.
tabletipe = dict([('ID.GA-1', '')])

# A list containing the names of the networks.
network_names = () 

# Dictionary composed of network names, and their respective ranges.
network_range = dict([])

ipdict = dict([])
path = os.getcwd()
ip = list()

# Removes [] from the string and returns the value in between.
def rm(org):
    res = str(org).split("[")
    res = res[1].split("]")
    res = res[0]

    return res

# Receives a list of values and removes ' from them, then it returns the output.
def rm2(org):
    res = str()
    for x in range(0, len(org)):
        if "AnsibleUndefined" in org[x] or "unknown" in org[x]:
            pass
        else:
            tmp = str(org[x]).split("'")
            tmp = tmp[1]

            if res == "":
                res += (tmp)
            else:
                res += (" / " + tmp)
    
    return res

# Adds | + values to ipdict dictionary.
def adddict(tip,add):
    for x in range(0, len(ip)):

        if ip[x] == tip:
            org = (str(ipdict[ip[x]]) + "|" + add)
            ipdict[ip[x]] = (org)

# Obtains FQDN of the main IP.
def host(IP):
    try:
        save = str(os.popen(f"host {IP}").read())
    except:
        pass
    else:
        temp = str()
        if "not found" in save:
            temp = str("null")
        else:
            save = save.split(" ")            
            save = str(save[(len(save) - 1)]).split(".")

            for i in range(0, (len(save) - 1)):
                if i != 0:
                    temp = str(temp + '.' + save[i])
                else:
                    temp = str(temp + save[i])

    return temp

# Function that removes "." of the IPs and returns them.
def convert_ipv4(ip):
    return tuple(int(n) for n in ip.split('.'))

# Function that compares the IP with the Network range.
def check_ipv4_in(addr, start, end):
    return convert_ipv4(start) <= convert_ipv4(addr) <= convert_ipv4(end)

# Function that attributes network or null to given IP.
def ListThem(ip, rede):
    for z in ip:
        for i in range(0, len(network_names)):
            x = tuple(network_range[network_names[i]])
            if check_ipv4_in(z, *x) == True:
                rede[z] = network_names[i]
                break   
            else:
                rede[z] = ""

try:
    file = str(sys.argv[1])
except:
    file = str(input("Input File: "))

try:
    save = str(sys.argv[2])
except:
    save = str(input("Output File: "))

filetosearch = (str(path) + '/' + file)
filetosave = (str(path) + '/' + save)

try:
    tempFile = open( filetosearch, 'r+' )
except:
    print(f"File \"{filetosearch}\" Can't Be Accessed!")
else:
    with tempFile:
        df = list(tempFile)
    
    for i in range(0, len(df)):
        if "TASK [Gathering Facts]" in df[i]:
            
            for z in range((i + 1), len(df)):
                if "TASK [hostname]" not in df[z]:            
                    if "ok:" in df[z]:
                        tip = rm(df[z])
                        ip.append(tip)
                else:
                    break

        elif "TASK [network info]" in df[i]:

            for z in range((i + 1), len(df)):
                if "TASK [mac info]" not in df[z]:
                    if "ok:" in df[z]:
                        tip = rm(df[z])
                    elif "All IPv4:" in df[z]:
                        src = rm(df[z]).split(",")
                        ipfour = rm2(src)
                    elif "All IPv6:" in df[z]:
                        src = rm(df[z]).split(",")
                        ipsix = rm2(src)

                        for x in range(0, len(ip)):
                            if ip[x] == tip:
                                h = host(ip[x])
                                ipdict[ip[x]] = (h + "|" + ipfour + "|" + ipsix)
                else:
                    break

        elif "TASK [mac info]" in df[i]:

            for z in range((i + 1), len(df)):
                if "TASK [OS and Kernel info]" not in df[z]:
                    if "ok:" in df[z]:
                        tip = rm(df[z])
                    elif "\"msg\": \"" in df[z]:
                        src = rm(df[z]).split(",")
                        mac = rm2(src)
                        adddict(tip, mac)
                    elif "\"msg\": [" in df[z]:
                        mac = str()
                        for x in range((z + 1), len(df)):
                            if "]" not in df[x]:
                                src = str(df[x]).split("\"")
                                src = src[1]
                                if mac == "":
                                    if src != "unknown" and src != "AnsibleUndefined":
                                        mac += (src)
                                else:
                                    if src != "unknown" and src != "AnsibleUndefined":
                                        mac += (" / " + src)
                            else:
                                break

                        adddict(tip, mac)
                else:
                    break

    rede = dict([])
    ListThem(ip, rede)

    for i in range(0, len(rede)):
        adddict(ip[i], rede[ip[i]])

try:
    tempFile = open( filetosave, 'w+' )
except:
    print(f"File \"{filetosave}\" Can't Be Accessed!")
else:
    writer = csv.writer(tempFile)
    writer.writerow([tabletipe['ID.GA-1']])

    for keys in ipdict.keys():
        temp = str(ipdict[keys]).split('|')

        for i in range(0, len(temp)):
            if temp[0] == "null":
                temp[0] = keys
            elif temp[i] == "null":
                temp[i] = ""
            
        domain = str(temp[0])
        ipv4 = str(temp[1])
        ipv6 = str(temp[2])
        mac = str(temp[3])
        network = str(temp[4])

        writer.writerow([domain, ipv4, ipv6, mac, network])