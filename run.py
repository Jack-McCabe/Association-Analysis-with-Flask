#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Jack McCabe

#Flask imports
from flask import Flask, render_template, flash, redirect, url_for, request
from wtforms import Form, StringField, validators
from fim import eclat
import pandas as pd

#initialize
app = Flask(__name__)

#Routes to inputform
@app.route('/')
def index():
    return render_template('inputform.html')


#%%
#Takes the inputs from inputforms and runs the assocaition analysis. It then spits out the output to rawcountrypid.html
@app.route('/rawcountrypid')
def rawcountrypid():
    country=request.args['country']
    pid= request.args['pid']
    data=eclatRules(ds,country)
    data= pd.DataFrame(data[data.iloc[:,0].str.contains(pid) ==True])
    return render_template('rawcountrypid.html', tables=[data.to_html(max_rows=15)], titles=['antecedants', 'consequents', 'support', 'confidence', 'list'])



 
#Gets called upond from userinputs, creates two fields for the user to input parameters
class InputForm(Form):
    country = StringField('Country (input  \'all\'  for every country)', [validators.Length(min=0, max=3)], default='all')
    pids = StringField('PID', [validators.Length(min=0, max=20)])

#gets the inputs from /inputform and gives to rawcoutry id 
@app.route('/inputform', methods=['GET', 'POST'])
def userInputs():
    #goes to class InputForm
    inputs = InputForm(request.form)
    if request.method == 'POST' and inputs.validate(): 
        country=inputs.country.data
        pid=inputs.pids.data
        flash('inputs taken')
        return redirect(url_for('rawcountrypid', country=country, pid=pid))
    return render_template('inputform.html', form=inputs)
 
 
#%%

#basic data management 
ds =  pd.read_csv('data_starting.csv.gz', compression='gzip') 
ds['ship_to_country']=ds['ship_to_country'].astype('str')
ds['order_number'] = ds['order_number'].astype('str')
ds['line_number'] = ds['line_number'].astype('str') 
ds['order_line']=  ds.loc[:, 'order_number'] + '-' + ds.loc[:, 'line_number']
#Removes OPT as they overcrowd the data source and are not important to the analysis
ds= pd.DataFrame(ds[ds['ordered_item'].str.contains('OPT') ==False])


#Runs the association analysis.
#eclat_result will have the antecedants, consequents, support, confidence and lift
def eclatRules(das, country):
    if country != 'all':
        das=das[das.ship_to_country.apply(lambda x: True if x in country else False)]
    das=das.groupby(['order_line'])['ordered_item'].apply(list).values.tolist()
    eclat_result=eclat(das, supp=10, zmax=4, report='aCL', target='r', eval='l')
    eclat_result=pd.DataFrame(eclat_result)
    eclat_result.columns=['antecedants', 'consequents', 'support', 'confidence', 'list']
    eclat_result.consequents=eclat_result.consequents.astype('str')
    eclat_result= eclat_result[eclat_result.consequents != '()']
    return eclat_result

 
#runs the app and creates a password incase you need to use sql backend DB
if __name__ == '__main__':
    app.secret_key='supersecured%pass***edword23'    
    app.run(debug=True) 
