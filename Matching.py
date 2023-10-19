import spacy, fitz,io
from database import mongo
from bson.objectid import ObjectId
from MediaWiki import get_search_results,get_summaries_for_queries
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
jd_model = spacy.load('assets/model_jd/model-best')
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


def Matching(user_id,job_id):
    print("Matching Started...")
    jd_data = JOBS.find_one({"_id":ObjectId(job_id)},{"FileData":1})["FileData"]
    # Check if jd_data is binary (PDF or DOCX)
    if isinstance(jd_data, bytes):
        with io.BytesIO(jd_data) as data:
            doc = fitz.open(stream=data)
            text_of_jd = " "
            for page in doc:
                text_of_jd = text_of_jd + str(page.get_text())
    else:
        # If jd_data is a string (plain text), assign it directly
        text_of_jd = jd_data


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
    print("Extracting from resume....")

    resume_jobpost = resumeFetchedData.find_one({"_id": ObjectId(user_id)}, {"JOBPOST": 1})["JOBPOST"]
    print("resume_jobpost: ",resume_jobpost)

    resume_experience_list = resumeFetchedData.find_one({"_id": ObjectId(user_id)}, {"EXPERIENCE": 1})["EXPERIENCE"]
    print("resume_experience: ",resume_experience_list)

    resume_skills = resumeFetchedData.find_one({"_id": ObjectId(user_id)}, {"SKILLS": 1})["SKILLS"]
    print("resume_skills: ",resume_skills)

    resume_text_only = resumeFetchedData.find_one({"_id": ObjectId(user_id)}, {"ResumeData": 1})["ResumeData"]
    print("Extraction completed from resume")


    ####################################
    print("Extracting from JD....")

    job_description_skills = dic_jd.get('SKILLS')
    print("job_description_skills: ",job_description_skills)

    jd_experience_list = dic_jd.get('EDUEXP')
    print("jd_experience_list: ",jd_experience_list)

    jd_post = dic_jd.get('JOBPOST')
    print("jd_post: ",jd_post)

    print("Extraction completed from JD")

    #############################################
    #########  Compare resume_jobpost and jd_post (10%)
    print("Comparing resume_jobpost and jd_post")
    jdpost_similarity = 0
    cos_jobpost_matching=0
    if jd_post and resume_jobpost:
        jd_post = [item.lower() for item in jd_post]

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
            cos_jobpost_matching = cos_jobpost_matching *0.1
    
            for i, item in enumerate(resume_jobpost):
                if item in jd_post:
                    result = True       
                else:
                    result = False                  
            if result == True:
                jdpost_similarity = 0.1
                cos_jobpost_matching = 0
            else:
                jdpost_similarity = cos_jobpost_matching
    else:
        jdpost_similarity = 0
    print("jd_post_simiarity:", jdpost_similarity)
    print("Completed Comparing resume_jobpost and jd_post")


    ########   compare resume_skills and jd_skills (30%)
    print("Comparing resume_skills and jd_skills")
    overall_skills_similarity= 0
    cos_skills_matching = 0

    if resume_skills and job_description_skills:
        new_resume_skills = []
        job_description_skills_text = ""
        resume_skills_text = ""
        resume_skills_text2 = ""
        cleaned_resume_skills_list = []

        if resume_skills:
            for skills in resume_skills: 
                cleaned_item = clean_text(skills)
                cleaned_resume_skills_list.append(cleaned_item)
                resume_skills_text += cleaned_item + " " 
                # search_query = f"{cleaned_item}"
                # try:     
                #     results = get_search_results(search_query)
                #     if results:
                #         new_resume_skills.append(results) 
                #     else:
                #         print("No matching articles found")
                # except ConnectionError as e:
                #     print(f"Connection Error: {e}")
                # except Exception as e:
                #     print(f"An error occurred: {e}")
                    
                # for new_skills in new_resume_skills:
                #     cleaned_item = clean_text(new_skills)
                #     resume_skills_text2 += cleaned_item + " " 
            search_queries = cleaned_resume_skills_list
            try:
                new_resume_skills = get_summaries_for_queries(search_queries)
            except ConnectionError as e:
                print(f"Connection Error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

            for new_skills in new_resume_skills:
                cleaned_item = clean_text(new_experience)
                resume_skills_text2 += cleaned_item + " "

        if job_description_skills:
            for skill in job_description_skills:
                cleaned_item = clean_text(skill)
                job_description_skills_text += cleaned_item + " "

            job_description_skills_text = job_description_skills_text.strip()
            resume_skills_text = resume_skills_text.strip()
            resume_skills_text2 = resume_skills_text.strip()
            cos_skills_matching1 = CosineMatching(resume_skills_text,job_description_skills_text)
            cos_skills_matching2 = CosineMatching(resume_skills_text2,job_description_skills_text)
            cos_skills_matching = cos_skills_matching1 + cos_skills_matching2
            cos_skills_matching = cos_skills_matching * 0.3
            overall_skills_similarity += cos_skills_matching
        else:
            overall_skills_similarity = 0
    else:
        overall_skills_similarity = 0
    print("SKills Matched:",overall_skills_similarity)
    print("Completed Comparing resume_skills and jd_skills")
    ##########################################
    # compare resume_experience and jd_experience
    print("Comparing resume_experience and jd_experience")
    new_resume_experience = []
    experience_similarity = 0
    cos_experience_matching = 0
    cleaned_resume_experience_list = []
    if resume_experience_list and jd_experience_list:
        job_description_experience_text = ""
        resume_experience_text = ""
        resume_experience_text2 = ""
        if resume_experience_list:
            for experience in resume_experience_list: 
                cleaned_item = clean_text(experience)
                cleaned_resume_experience_list.append(cleaned_item)
                resume_experience_text += cleaned_item + " " 
                # search_query = f"{cleaned_item}"
                # try:
                #     results = get_search_results(search_query)
                #     if results:
                #         new_resume_experience.append(results) 
                #     else:
                #         print("No matching articles found")
                # except ConnectionError as e:
                #     print(f"Connection Error: {e}")
                # except Exception as e:
                #     print(f"An error occurred: {e}")

                # for new_experience in new_resume_experience:
                #     cleaned_item = clean_text(new_experience)
                #     resume_experience_text2 += cleaned_item + " "
            search_queries = cleaned_resume_experience_list
            try:
                new_resume_experience = get_summaries_for_queries(search_queries)
            except ConnectionError as e:
                print(f"Connection Error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

            for new_experience in new_resume_experience:
                cleaned_item = clean_text(new_experience)
                resume_experience_text2 += cleaned_item + " "
        
        if jd_experience_list:
            for experience in jd_experience_list: 
                cleaned_item = clean_text(experience)
                job_description_experience_text += cleaned_item + " " 
        
        resume_experience_text = resume_experience_text.strip()
        resume_experience_text2 = resume_experience_text2.strip()
        job_description_experience_text = job_description_experience_text.strip()
        cos_experience_matching1 = CosineMatching(resume_experience_text,job_description_experience_text)
        cos_experience_matching2 = CosineMatching(resume_experience_text2,job_description_experience_text)
        cos_experience_matching = cos_experience_matching1 + cos_experience_matching2
        if(cos_experience_matching > 1):
            cos_experience_matching = 1
        cos_experience_matching = cos_experience_matching * 0.6
        experience_similarity += cos_experience_matching
    else:
        experience_similarity = 0
    print("experience_matching:",experience_similarity)
    

    finalsimilarity = 0
    finalsimilarity = CosineMatching(resume_text_only ,text_of_jd)
    finalsimilarity = finalsimilarity * 0.3
    matching = 0
    matching=(jdpost_similarity + experience_similarity+ overall_skills_similarity)*100
    if (matching <= 0.3):
        final_matching= (jdpost_similarity + experience_similarity+ overall_skills_similarity+finalsimilarity)*100
        matching += final_matching
    matching = round(matching,2)
    print("Overall Similarity between resume and jd is ",matching )
    return matching;