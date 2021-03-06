# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 10:50:40 2020

@author: YJ001
"""
import pandas as pd
import statsmodels.formula.api as smf
from sys import argv
from hdfs.client import Client


def quantile_reg(df, quantile):
    mod = smf.quantreg(df.columns[1] + '~' + df.columns[0], df)
    res = mod.fit(q = quantile)
    print(res.summary())
#    get_y = lambda a, b: a + b * df.iloc[:,0].values
#    pre_y = get_y(res.params[0], res.params[1])
    qre_df = pd.DataFrame(data = [[quantile, res.params[0], res.params[1]] + res.conf_int().iloc[1].tolist()], 
                               index = ['quantile_reg'], 
                               columns = ['qt','intercept','x_coef','cf_lower_bound','cf_upper_bound',])
    return qre_df 

def get_parameter():
    print ("length:{}, content：{}".format(len(argv),argv))
    file_path = argv[argv.index('--file_path')+1]
  
    if "--quantile" not in argv:        
        quantile = 0.5
    else:
        quantile = float("%.1f"%float(argv[argv.index('--quantile')+1])) 
    if "--outpath" not in argv:
        outpath = None
    else:
        outpath = argv[argv.index('--outpath')+1]    
    return file_path, quantile, outpath

def get_data_hdfs(file_path):    
    HDFSUrl = "http://192.168.0.201:50070"
    client = Client(HDFSUrl, root='/')
    with client.read(file_path, buffer_size=1024, delimiter='\n', encoding='utf-8') as reader:
        data = [line.strip().split() for line in reader]
        print("data",data[0:5])
    df = pd.DataFrame(data[1:],columns=data[0])
    return df

def dataframe_write_to_hdfs(hdfs_path, dataframe):
    """
    :param client:
    :param hdfs_path:
    :param dataframe:
    :return:
    """
    HDFSUrl = "http://192.168.0.201:50070"
    client = Client(HDFSUrl, root='/')    
    client.write(hdfs_path, dataframe.to_csv(header=False,index=False,sep="\t"), encoding='utf-8',overwrite=True)
    
def main(file_path, quantile, outpath): 
    try:
        df = get_data_hdfs(file_path)
    except Exception as e:
        print(e,'Can not get data from hdfs, use test data from local' )
        df = pd.read_csv(file_path)  #
    res = quantile_reg(df, quantile)
    print(res)
    if outpath != None:
        dataframe_write_to_hdfs(outpath, res)
    else:
        res.to_csv('C:/Users/YJ001/Desktop/project/algorithm/test_data/output/qrg_res.csv')
    return res
 


if __name__=="__main__":
    #local test 
#    df = pd.DataFrame({'x':[20.5, 19.8, 19.7, 20.4, 20.1, 20.0, 19.0, 19.9],'y':[20.7, 19.8, 19.5, 20.8, 20.4, 19.6, 20.2, 20.3]})
#    quantile =.5
#    res = main(df, quantile)
    
    file_path, quantile, outpath = get_parameter()
    res = main(file_path, quantile, outpath)
    cmd = "python quantile_reg.py --file_path C:/Users/YJ001/Desktop/project/algorithm/test_data/input/qrg_test.csv --quantile 0.5"