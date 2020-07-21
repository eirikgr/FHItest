#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import datetime

# Population in municiplaities in norway since 1986
info = pd.read_csv('./26975.csv')
# Codes for the counties in Norway
county = pd.read_csv('./county.csv',sep=";")

# Adding some extra information, handy when extracting info based on municipality code later
info['location_code'] = info.apply(lambda row: (row.region.split()[0]).replace('K-',''), axis = 1)
info['location_name'] = info.apply(lambda row: (row.region.split()[1].strip()), axis = 1)

if not os.path.exists('/output/'):
    os.makedirs('/output/')

def formatNumber(numb):
    ls = [str(s) for s in str(numb) if s.isdigit()]
    if len(ls) <= 4:
        return str(numb)
    else:
        subtr = []
        nl = 0
        subl = ""
        for l in reversed(ls):
            subl = l+subl
            if (nl+1)%3 == 0 and nl > 0:
                subtr.append(subl)
                subl = ""
            nl += 1
        if subl:
            subtr.append(subl)
    return " ".join(reversed(subtr))
            
    
def createDir(fname):
    if not os.path.exists(fname):
        os.makedirs(fname)

def get_munip_county(munip):
    munip_id  = "".join([str(s) for s in munip if s.isdigit()])
    county_id = "".join([str(s) for s in munip if s.isdigit()][0:2])
    return munip_id, int(county_id)

def get_population(munip):
    num = "".join([str(s) for s in munip if s.isdigit()])
    #dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    #yr = dt.year

    dummy = info.loc[(info.location_code == num)]

    info_dict = dict(zip(dummy.year, dummy["07459: Population, by region, year and contents"]))

    return info_dict
    #['07459: Population, by region, year and contents']
    
    #try:
   #     return info.loc[(info.location_code == num) & (info.year == int(yr))]['07459: Population, by region, year and contents'].iloc[0]
    #except:
    #    print "Could not find population for municipality %s" %code
    #    return -1


# verbosity
vb = 0

df = pd.read_csv('/input/individual_level_data.csv')

#info['nump'] = info.apply(lambda row: (int(row.value.split()[0])), axis = 1)

#sys.exit()

un_dates = df['date'].unique()
#for i in range(2033,2055):
#un_dates = un_dates[0:2033]#drop(df.index[i])
un_locat = df['location_code'].unique()

#full_day  = pd.DataFrame(columns=["location_code","location_name","date","num_sick","num_population","county_code","isoyearweek"])
full_week = pd.DataFrame(columns=["location_code","location_name","isoyearweek","num_sick","num_population"])

nentry = 0
nentry2 = 0
nlocat = 0
for locat in un_locat:

    print("Doing municipality %i/%i" %(nlocat,len(un_locat)))
    
    munip_id, county_id = get_munip_county(locat)

    munip_name  = info.loc[info.location_code == munip_id]['location_name'].iloc[0]
    county_name = county.loc[county.code == county_id]['name'].iloc[0]

    # create entry for county too (if not done already)
    county_code = "county%02d" %county_id
    
    # get info for this municipality (from SSB info)
    munip_info = get_population(locat)

    # make dummy data frame for further manipulation
    dummy = df.loc[df['location_code'] == locat]
    count = dummy.groupby('date',as_index=False).agg(['count'])
    dummy.drop_duplicates('date',inplace=True)
    dummy.reset_index(inplace=True)
    un_dates = list(dummy['date'])
    dummy['num_sick'] = pd.Series(list(count["value"]["count"]),index=dummy.index)
    dummy['location_name'] = pd.Series(munip_name,index=dummy.index)
    dummy['county_code'] = pd.Series(county_code,index=dummy.index)
    dummy['num_population'] = dummy.apply(lambda row: (munip_info[int(datetime.datetime.strptime(row.date,'%Y-%m-%d').year)]), axis = 1)
    dummy['isoyearweek'] = dummy.apply(lambda row: ("%s-%02d"%(datetime.datetime.strptime(row.date,'%Y-%m-%d').isocalendar()[0],datetime.datetime.strptime(row.date,'%Y-%m-%d').isocalendar()[1])), axis = 1)

    dummy.drop("value",axis=1)
    dummy.drop("index",axis=1)
    
    
    try:
        full_day = pd.concat([full_day,dummy],axis=0)
    except:
        full_day = dummy
        


    
    # loop over unique days in data range
    nlocat += 1
    ndate = 0

    #sys.exit()
    
    # for date in un_dates:

    #     if ndate%100 == 0: print("Doing date %i/%i" %(ndate,len(un_dates)))
        
    #     # get year
    #     dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    #     yr = int(dt.year)

    #     if not yr in munip_info.keys():
    #         print("Could not find population from %i for %s" %(yr,munip_name))
    #         continue

    #     # extract information
    #     pop   = munip_info[yr]
    #     nsick = dummy[dummy['date'] == date].shape[0]
        
    #     if vb: print("Sick people in municipality %s on date %s is %i" %(locat,date,nsick))

    #     isoyearweek = "%s-%02d" %(dt.isocalendar()[0],dt.isocalendar()[1])
        
    #     full_day.loc[nentry] = pd.Series({'location_code':locat, 'location_name':munip_name, 'date':date, 'num_sick':nsick, 'num_population':pop, 'county_code':county_code, 'isoyearweek':isoyearweek})
    #     nentry += 1

    #     try:
    #         full_day.at[full_day.loc[(full_day.location_code == county_code) & (full_day.date == date)].index[0],'num_sick'] += nsick
    #         full_day.at[full_day.loc[(full_day.location_code == county_code) & (full_day.date == date)].index[0],'num_population'] += pop
    #     except:
    #         full_day.loc[nentry] = pd.Series({'location_code':county_code, 'location_name':county_name, 'date':date, 'num_sick':nsick, 'num_population':pop, 'county_code':county_code, 'isoyearweek':isoyearweek})
    #         nentry += 1
            
    #     try:
    #         full_day.at[full_day.loc[(full_day.location_code == "norge") & (full_day.date == date)].index[0],'num_sick'] += nsick
    #         full_day.at[full_day.loc[(full_day.location_code == "norge") & (full_day.date == date)].index[0],'num_population'] += pop
    #     except:
    #         full_day.loc[nentry] = pd.Series({'location_code':"norge", 'location_name':"Norge", 'date':date, 'num_sick':nsick, 'num_population':pop, 'county_code':'norge', 'isoyearweek':isoyearweek})
    #         nentry += 1
            
    #     ndate += 1
    #     if ndate > 10: break
    #     #break
        
    un_isoyw = full_day['isoyearweek'].unique()
    for isoyw in un_isoyw:
        nsick = full_day.loc[(full_day.isoyearweek == isoyw) & (full_day.location_code == locat)]["num_sick"].sum()
        full_week.loc[nentry2] = pd.Series({'location_code':locat,"location_name":munip_name,"isoyearweek":isoyw,"num_sick":nsick,"num_population":munip_info[int(isoyw.split("-")[0])]})
        nentry2 += 1
    #if nlocat > 3: break




full_day.drop("index",axis=1)
full_day.drop("value",axis=1)

dummy = pd.DataFrame(data = {'date': pd.Series(list(un_dates))})
dummy['num_sick'] = pd.Series(list(full_day.groupby('date',as_index=False).agg(['sum'])["num_sick"]["sum"]))
dummy['location_name'] = pd.Series("Norge",index=dummy.index)
dummy['location_code'] = pd.Series("norge",index=dummy.index)
dummy['county_code'] = pd.Series("norge",index=dummy.index)
dummy['num_population'] = pd.Series(list(full_day.groupby('date',as_index=False).agg(['sum'])["num_population"]["sum"]))
dummy['isoyearweek'] = dummy.apply(lambda row: ("%s-%02d"%(datetime.datetime.strptime(row.date,'%Y-%m-%d').isocalendar()[0],datetime.datetime.strptime(row.date,'%Y-%m-%d').isocalendar()[1])), axis = 1)
full_day = pd.concat([full_day,dummy],axis=0)

# Filling inoformation about norway
#for isoyw in un_isoyw:
#    nsick = full_day.loc[(full_day.isoyearweek == isoyw) & (full_day.location_code == "norge")]["num_sick"].sum()
#    pop   = full_day.loc[(full_day.isoyearweek == isoyw) & (full_day.location_code == "norge")]["num_population"].iloc[0]
#    full_week.loc[nentry2] = pd.Series({'location_code':"norge","location_name":"Norge","isoyearweek":isoyw,"num_sick":nsick,"num_population":pop})
#    nentry2 += 1

#un_countyc = full_day['county_code'].unique()
#un_countyc = [3, 11, 15, 18, 30, 34, 38, 42, 46, 50, 54, 99]
un_countyc = full_day['county_code'].unique()
for countycode in un_countyc:
    if type(countycode) == int:
        countyc = 'county%02d' %countycode
    else: countyc = countycode
    
    if not countyc: continue
    
    if not "norge" in countyc:
        munip_id, county_id = get_munip_county(countyc)
        county_name = county.loc[county.code == county_id]['name'].iloc[0]
        county_name = county_name.split("-")[0]
    else:
        county_name = "Norge"

    dummy = pd.DataFrame(data = {'date': pd.Series(list(un_dates))})
    dummy['num_sick'] = pd.Series(list(full_day.loc[(full_day.county_code == countyc)].groupby('date',as_index=False).agg(['sum'])["num_sick"]["sum"]))
    dummy['location_name'] = pd.Series(county_name,index=dummy.index)
    dummy['location_code'] = pd.Series(countyc,index=dummy.index)
    dummy['county_code'] = pd.Series(countyc,index=dummy.index)
    dummy['num_population'] = pd.Series(list(full_day.loc[(full_day.county_code == countyc)].groupby('date',as_index=False).agg(['sum'])["num_population"]["sum"]))
    dummy['isoyearweek'] = dummy.apply(lambda row: ("%s-%02d"%(datetime.datetime.strptime(row.date,'%Y-%m-%d').isocalendar()[0],datetime.datetime.strptime(row.date,'%Y-%m-%d').isocalendar()[1])), axis = 1)
    full_day = pd.concat([full_day,dummy],axis=0)
    
    fname = '/output/%s' %county_name

    # filling information about counties
    for isoyw in un_isoyw:
        nsick = full_day.loc[(full_day.isoyearweek == isoyw) & (full_day.location_code == countyc)]["num_sick"].sum()
        pop   = full_day.loc[(full_day.isoyearweek == isoyw) & (full_day.location_code == countyc)]["num_population"].iloc[0]
        full_week.loc[nentry2] = pd.Series({'location_code':countyc,"location_name":county_name,"isoyearweek":isoyw,"num_sick":nsick,"num_population":pop})
        nentry2 += 1
    
    createDir(fname)
    
    if county_name == "Norge":
        full_day.loc[(full_day.location_code == "norge")].to_excel("%s/full_day.xlsx"%(fname),columns=["location_code","location_name","date","num_sick","num_population"])
        full_week.loc[(full_week.location_code == "norge")].to_excel("%s/full_week.xlsx"%(fname),columns=["location_code","location_name","isoyearweek","num_sick","num_population"])

        # Do the plotting
        ax = full_day[(full_day.location_code == "norge")].plot(y="num_sick",x="date",kind="line",grid=True,
                                                               label="Disease X in %s (pop. %s)"%("Norge",formatNumber(full_day[(full_day.location_code == countyc)]["num_population"].iloc[0])))
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of sick persons")
        #fig = plt.figure()
        plt.savefig("%s/graph.png"%(fname))
        
        continue
    
    createDir(fname+"/_county")

    full_day.loc[(full_day.location_code == countyc)].to_excel("%s/_county/full_day.xlsx"%fname,columns=["location_code","location_name","date","num_sick","num_population"])
    full_week.loc[(full_week.location_code == countyc)].to_excel("%s/_county/full_week.xlsx"%fname,columns=["location_code","location_name","isoyearweek","num_sick","num_population"])

    # Do the plotting
    ax = full_day[(full_day.location_code == countyc)].plot(y="num_sick",x="date",kind="line",grid=True,
                                                               label="Disease X in %s (pop. %s)"%(county_name,formatNumber(full_day[(full_day.location_code == countyc)]["num_population"].iloc[0])))
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of sick persons")
    #fig = plt.figure()
    plt.savefig("%s/_county/graph.png"%(fname))
    
    for munip_code, munip in zip(full_day.loc[(full_day.county_code == countyc)]["location_code"].unique(),full_day.loc[(full_day.county_code == countyc)]["location_name"].unique()):

        newfname = "%s/%s"%(fname,munip)
        
        #print newfname
        createDir(newfname)
        
        # Saving into directory
        full_day.loc[(full_day.location_code == munip_code)].to_excel("%s/full_day.xlsx"%(newfname),columns=["location_code","location_name","date","num_sick","num_population"])
        full_week.loc[(full_week.location_code == munip_code)].to_excel("%s/full_week.xlsx"%(newfname),columns=["location_code","location_name","isoyearweek","num_sick","num_population"])

        # Do the plotting
        ax = full_day[(full_day.location_code == munip_code)].plot(y="num_sick",x="date",kind="line",grid=True,
                                                                   label="Disease X in %s (pop. %s)"%(munip,formatNumber(full_day[(full_day.location_code == munip_code)]["num_population"].iloc[0])))
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of sick persons")
        #fig = plt.figure()
        plt.savefig("%s/graph.png"%(newfname))
#full_day.to_excel("full_day.xlsx",columns=["location_code","location_name","date","num_sick","num_population"])

full_day.to_excel("/output/full_day.xlsx",columns=["location_code","location_name","date","num_sick","num_population"])
# done with full_week, writing to file
full_week.to_excel("/output/full_week.xlsx",columns=["location_code","location_name","isoyearweek","num_sick","num_population"])
