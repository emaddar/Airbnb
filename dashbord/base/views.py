from django.shortcuts import render

import pandas as pd
import re


# Create your views here.
def home_view(request):
    return render(request, "index.html")


def result(request):
    city = request.GET['ville']                                # Get ville
    df = pd.read_csv(f"../pandas/CSV/{city.lower()}/listings_{city.lower()}.csv")
    df_reviews = pd.read_csv(f"../pandas/CSV/{city.lower()}/reviews_{city.lower()}.csv")

    q1 = df.groupby("neighbourhood_cleansed").apply(lambda s: pd.Series({ 
    "host count": s["host_id"].nunique(), 
    "sum reviews": s["number_of_reviews"].sum(), 
        }))

    df_host_acceptance_rate = df["host_acceptance_rate"].str.rstrip('%').astype(float)

    accept_rate = round(df_host_acceptance_rate.mean(),2)

    df_host_response_rate = df["host_response_rate"].str.rstrip('%').astype(float)

    response_rate = round(df_host_response_rate.mean(),2)

    df.replace(to_replace="work_email", value='work', regex=True,inplace=True)
    email = df["host_verifications"].apply(lambda elt: 1 if 'email' in elt else 0 ).sum()
    email_pourcent = round(email/len(df)*100,2)
    phone = df["host_verifications"].apply(lambda elt: 1 if 'phone' in elt else 0 ).sum()
    phone_pourcent = round(phone/len(df)*100,2)
    work = df["host_verifications"].apply(lambda elt: 1 if 'work' in elt else 0 ).sum()
    work_pourcent = round(work/len(df)*100,2)
    vide = df["host_verifications"].apply(lambda elt: 1 if elt == "[]" else 0 ).sum()
    vide_pourcent = round(vide/len(df)*100,2)


    df["np_amenities"] =  df['amenities'].apply(lambda elt: re.sub("\[|\]|\"","",elt))
    df["np_amenities"] = df["np_amenities"].apply(lambda elt: elt.split(","))
    df["np_amenities"] =  df["np_amenities"].apply(lambda x: len(x))
    amenities = df[["np_amenities","room_type"]].groupby('room_type').agg(["mean","std"])


    df["price"]= df["price"].str.replace(',',"")
    df["price"]= df["price"].str.replace('$',"").astype(float)
    
    def quartile1(x):
        return x.quantile(0.25)
    def quartile3(x):
        return x.quantile(0.75)
    q5 = df[["price","room_type"]].groupby('room_type').agg(["median","max","min",quartile1,quartile3])



    def first(s):
        return(re.findall("\d+\.\d+|\d+", s))

    def last(s):
        return(re.split('(\d+)', s)[-1])
    
    df['number_bath'] = df['bathrooms_text'].apply(lambda x :  first(str(x)))
    df['bath_describe'] = df['bathrooms_text'].apply(lambda x : last(str(x)))
    df['number_bath'] = pd.DataFrame([x for x in df['number_bath'] ]) # remove list from N

    mask = df["bath_describe"] == "nan"
    df[mask]
    df_clean = df.drop(df[mask].index)

    df_clean['number_bath'] =df_clean['number_bath'].apply(lambda x: 1 if (x is None) else float(x))
    df_clean["bath_describe"]=df_clean["bath_describe"].str.lower()

    df_clean['private'] = df_clean['bath_describe'].apply(lambda x: 2 if ("private" in x) else 1)
    df_clean['shared'] = df_clean['bath_describe'].apply(lambda x: 0.5 if ("shared" in x) else 1)
    df_clean['half_bath'] = df_clean['bath_describe'].apply(lambda x: 0.5 if ("half-bath" in x) else 1)

    df_clean['number_bath'] = (df_clean['number_bath'] * df_clean['half_bath']) * df_clean['private']*df_clean['shared']

    q6 = df_clean[["host_id","number_bath"]].groupby("number_bath").count()

    df_simple = df[["number_of_reviews",'description']]
    df_simple["len_description"] = df_simple['description'].apply(lambda x: len(str(x)))
    
    q7=df_simple["number_of_reviews"].corr(df_simple['len_description'])
    
    df_reviews.columns=['Unnamed: 0', 'listing_id', 'id_review', 'date', 'reviewer_id', 'reviewer_name']
    df_reviews= df_reviews[['listing_id', 'id_review', 'date', 'reviewer_id',
    'reviewer_name']]
    df_merge = df_reviews.merge(df, how='left',left_on='listing_id',right_on='id') 
    mask = df_merge["host_name"] ==df_merge["reviewer_name"]
    q8=len(df_merge[["host_name","reviewer_name"]][mask])/len(df_merge)*100
    return render(request, 'result.html', {
                                            'city':city,
                                            'q1': q1.reset_index().to_html,
                                            'accept_rate' : accept_rate,
                                            'response_rate' : response_rate,
                                            'email' : email,
                                            'email_pourcent' : email_pourcent,
                                            'phone' : phone,
                                            'phone_pourcent' : phone_pourcent,
                                            'work' : work,
                                            'work_pourcent' : work_pourcent,
                                            'vide' : vide,
                                            'vide_pourcent' : vide_pourcent,
                                            'amenities' : amenities.reset_index().to_html,
                                            'q5' : q5.reset_index().to_html,
                                            'q6' : q6.reset_index().to_html,
                                            'q7' : round(q7,2),
                                            'q8' : round(q8,2),
                                            
                })