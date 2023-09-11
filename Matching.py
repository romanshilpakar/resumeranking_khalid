import spacy, fitz,io
from flask import  session,request
from database import mongo
from bson.objectid import ObjectId
from MediaWiki import get_search_results
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
punctuation = string.punctuation



resumeFetchedData = mongo.db.resumeFetchedData
JOBS = mongo.db.JOBS


###Spacy model
print("Loading Jd Parser model...")
jd_model = spacy.load('assets/JdModel/output/model-best')
print("Jd Parser model loaded")


def clean_text(text):
    # Tokenize the text into words
    words = nltk.word_tokenize(text)

    # Remove stopwords and punctuation
    filtered_words = [word.lower() for word in words if word.lower() not in stop_words and word not in punctuation]

    # Join the filtered words into a single string
    cleaned_text = " ".join(filtered_words)

    return cleaned_text

def CosineMatching(cv_text,jd_text):
    text=[cv_text,jd_text]
    cv=CountVectorizer()
    count_matrix=cv.fit_transform(text)
    matchper=cosine_similarity(count_matrix)[0][1]
    return round(matchper,2)


def Matching():
    job_id = request.form['job_id']
    jd_data = JOBS.find_one({"_id":ObjectId(job_id)},{"FileData":1})["FileData"]
    with io.BytesIO(jd_data) as data:
        doc = fitz.open(stream=data)
        text_of_jd = " "
        for page in doc:
            text_of_jd = text_of_jd + str(page.get_text())


    label_list_jd=[]
    text_list_jd = []
    dic_jd = {}

    doc_jd = jd_model(text_of_jd)
    for ent in doc_jd.ents:
        label_list_jd.append(ent.label_)
        text_list_jd.append(ent.text)

    print("Model work done")

    for i in range(len(label_list_jd)):
        if label_list_jd[i] in dic_jd:
            # if the key already exists, append the new value to the list of values
            dic_jd[label_list_jd[i]].append(text_list_jd[i])
        else:
            # if the key does not exist, create a new key-value pair
            dic_jd[label_list_jd[i]] = [text_list_jd[i]]

    print("Jd dictionary:",dic_jd)


    resume_jobpost = resumeFetchedData.find_one({"UserId": ObjectId(session['user_id'])}, {"JOB POST": 1})["JOB POST"]
    print("resume_jobpost: ",resume_jobpost)

    resume_experience_list = resumeFetchedData.find_one({"UserId": ObjectId(session['user_id'])}, {"EXPERIENCE": 1})["EXPERIENCE"]
    print("resume_experience: ",resume_experience_list)
    # resume_experience = []
    # for p in resume_experience_list:
    #     parts = p.split()
    #     if "years" in p or "year" in p:
    #         year = int(parts[0])
    #         if "months" in p or "month" in p:
    #             year += int(parts[2]) / 12
    #     else:
    #         year = int(parts[0]) / 12
    #     year = round(year, 2)
    #     resume_experience.append(year)

    # print("resume_experience: ",resume_experience)

    resume_skills = resumeFetchedData.find_one({"UserId": ObjectId(session['user_id'])}, {"SKILLS": 1})["SKILLS"]
    print("resume_skills: ",resume_skills)

    resume_education = resumeFetchedData.find_one({"UserId": ObjectId(session['user_id'])}, {"EDUCATION": 1})["EDUCATION"]
    print("resume_education: ",resume_education)

    resume_certification = resumeFetchedData.find_one({"UserId": ObjectId(session['user_id'])}, {"CERTIFICATION": 1})["CERTIFICATION"]
    print("resume_certification: ",resume_certification)

    resume_text_only = resumeFetchedData.find_one({"UserId": ObjectId(session['user_id'])}, {"ResumeData": 1})["ResumeData"]
    # print("resume_text_only: ",resume_text_only)
    # print("jd_text_only: ",text_of_jd)

    ####################################

    job_description_skills = dic_jd.get('SKILLS')
    print("job_description_skills: ",job_description_skills)

    job_description_education = dic_jd.get('EDUCATION')
    print("job_description_education: ",job_description_education)

    jd_experience_list = dic_jd.get('EXPERIENCE')
    print("jd_experience_list: ",jd_experience_list)

    # jd_experience = []
    # for p in jd_experience_list:
    #     parts = p.split()
    #     if "years" in p or "year" in p:
    #         year = int(parts[0])
    #         if "months" in p or "month" in p:
    #             year += int(parts[2]) / 12
    #     else:
    #         year = int(parts[0]) / 12
    #     year = round(year, 2)
    #     jd_experience.append(year)

    # print("jd_experience: ",jd_experience)

    jd_post = dic_jd.get('JOB POST')
    print("jd_post: ",jd_post)


    #############################################
    #########  Compare resume_jobpost and jd_post
    jd_post = [item.lower() for item in jd_post]
    experience_similarity = 0
    match_index = -1
    jdpost_similarity = 0
    cos_jobpost_matching=0
    job_description_jobpost_text = ""
    resume_jobpost_text = ""
    if resume_jobpost:
        resume_jobpost = [item.lower() for item in resume_jobpost]

        for items in resume_jobpost: 
            cleaned_item = clean_text(items)
            resume_jobpost_text += cleaned_item + " "
        for items in jd_post: 
            cleaned_item = clean_text(items)
            job_description_jobpost_text += cleaned_item + " "
        job_description_jobpost_text = job_description_jobpost_text.strip()
        resume_jobpost_text = resume_jobpost_text.strip()
        cos_jobpost_matching = CosineMatching(resume_jobpost_text,job_description_jobpost_text)
        cos_jobpost_matching = cos_jobpost_matching *0.2
    
        # for i, item in enumerate(resume_jobpost):
        #     if item in jd_post:
        #         result = True
        #         match_index = i
        #         ########   compare resume_experience and jd_experience
        #         if resume_experience:
        #             experience_difference = (jd_experience[0] - resume_experience[match_index])
        #             if (experience_difference <= 0):
        #                 print("Experience Matched")
        #                 experience_similarity = 1
        #             elif (0 < experience_difference <= 1):
        #                 print("Experience  can be considered")
        #                 experience_similarity = 0.7
        #             else:
        #                 print("Experience  Unmatched")
        #                 experience_similarity = 0
                
        #             break
        #     else:
        #         result = False
                
        # if result == True:
        #     jdpost_similarity = 1
        # else:
        #     jdpost_similarity = 0

    jdpost_similarity = jdpost_similarity * 0.3
    jdpost_similarity += cos_jobpost_matching
    # print("jd_post_simiarity: ", jdpost_similarity)
    experience_similarity = experience_similarity * 0.2
    # print("Experiece Similarity: ", experience_similarity)



    ########   compare resume_skills and jd_skills

    new_resume_skills = []
    count = 0
    overall_skills_similarity= 0
    job_description_skills_text = ""
    resume_skills_text = ""

    if resume_skills:
        for skills in resume_skills: 
            cleaned_item = clean_text(skills)
            resume_skills_text += cleaned_item + " "  
            search_query = f"{skills} in technology "
            results = get_search_results(search_query)
            if results:
                new_resume_skills.append(results) 
            else:
                print("No matching articles found")

    if job_description_skills:
        for skill in job_description_skills:
            cleaned_item = clean_text(skill)
            job_description_skills_text += cleaned_item + " "
            for resume_skill in new_resume_skills:
                if skill in resume_skill:
                    count += 1
                    break

        skills_similarity = 1 - ((len(job_description_skills) - count)/ len(job_description_skills))
        # print("skills_similarity_jacard:",skills_similarity)
        skills_similarity = skills_similarity * 0.6
        # overall_skills_similarity += skills_similarity
        job_description_skills_text = job_description_skills_text.strip()
        resume_skills_text = resume_skills_text.strip()
        cos_skills_matching = CosineMatching(resume_skills_text,job_description_skills_text)
        # print("skills_similarity_consile:",cos_skills_matching)
        cos_skills_matching = cos_skills_matching * 0.2
        overall_skills_similarity = overall_skills_similarity + skills_similarity +cos_skills_matching
        # print("SKills Matched:",overall_skills_similarity)

    else:
        skills_similarity = 0
        # print("Skills Matched", skills_similarity)

    
    ########   compare resume_education and jd_education
    

    new_resume_education = []
    count = 0
    overall_education_similarity= 0
    job_description_education_text = ""
    resume_education_text = ""
    if resume_education:
        for educations in resume_education:
            cleaned_item = clean_text(educations)
            resume_education_text += cleaned_item + " "   
            search_query = f"{educations} in technology "
            results = get_search_results(search_query)
            if results:
                new_resume_education.append(results) 
            else:
                print("No matching articles found")

    if job_description_education:
        for educations in job_description_education:
            cleaned_item = clean_text(educations)
            job_description_education_text += cleaned_item + " "
            for resume_education in new_resume_education:
                if educations in resume_education:
                    count += 1
                    break

        education_similarity =1 - ((len(job_description_education) - count)/ len(job_description_education))
        education_similarity = education_similarity * 0.3

        job_description_education_text = job_description_education_text.strip()
        resume_education_text = resume_education_text.strip()
        cos_education_matching = CosineMatching(resume_education_text,job_description_education_text)
        cos_education_matching = cos_skills_matching *0.1
        overall_education_similarity = overall_education_similarity + education_similarity + cos_education_matching
        # print("EDUCATION Matched:",overall_education_similarity)

    else:
        education_similarity = 0
        # print("EDUCATION Matched", education_similarity)


    # WORKING TILL HERE




    #### Certification Similarity
    
    job_description_skill_education_experience_text = ""
    resume_certification_text = ""

    if resume_certification:
        for item in resume_certification:
            cleaned_item = clean_text(item)
            resume_certification_text += cleaned_item + " "

    if job_description_skills:
        for item in job_description_skills:
            cleaned_item = clean_text(item)
            job_description_skill_education_experience_text += cleaned_item + " "
    
    if jd_experience_list:
        for item in jd_experience_list:
            cleaned_item = clean_text(item)
            job_description_skill_education_experience_text += cleaned_item + " "
    
    if job_description_education:
        for item in job_description_education:
            cleaned_item = clean_text(item)
            job_description_skill_education_experience_text += cleaned_item + " "
    
    
    job_description_skill_education_experience_text = job_description_skill_education_experience_text.strip()
    resume_certification_text = resume_certification_text.strip()

    certification_matching = CosineMatching(resume_certification_text,job_description_skill_education_experience_text)
    certification_matching = certification_matching * 0.2
    # print("Certification_matching:",certification_matching)

    ##########################################
    finalsimilarity = CosineMatching(resume_text_only ,text_of_jd)
    finalsimilarity = finalsimilarity * 0.25

    matching=(jdpost_similarity + experience_similarity+  overall_skills_similarity + overall_education_similarity +  certification_matching+finalsimilarity)*100
    matching = round(matching,2)
    print("Overall Similarity between resume and jd is ",matching )

    return matching;



