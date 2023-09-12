from flask import Blueprint, render_template, request, redirect
from werkzeug.utils import secure_filename
import os,fitz,spacy,docx2txt
from bson.objectid import ObjectId
from database import mongo
from datetime import datetime
from Matching import Matching



job_post = Blueprint("Job_post", __name__, static_folder="static", template_folder="templates")

jd_folder = "static/uploaded_jd/"
resume_folder = "static/uploaded_resumes/"

JOBS = mongo.db.JOBS
Applied_EMP = mongo.db.Applied_EMP
resumeFetchedData = mongo.db.resumeFetchedData
IRS_USERS = mongo.db.IRS_USERS

###Spacy model
print("Loading Resume Parser model...")
nlp = spacy.load('assets/ResumeModel/output/model-best')
print("Resume Parser model loaded")

def allowedExtension(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ['docx','pdf']

def extractData(file,ext):
    text=""
    if ext=="docx": 
        temp = docx2txt.process(file)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        text = ' '.join(text)
    elif ext == "pdf":
        for page in fitz.open(file):
            text += page.get_text()
        text = " ".join(text.split('\n'))
    
    elif ext == "txt":
        with open(file, 'r', encoding='utf-8') as txt_file:
            text = txt_file.read()
    return text

def resume_extraction(filename,jd_id):
    fname = "static/uploaded_resumes/"+filename
    print(fname)
    doc = fitz.open(fname)
    print("Resume taken as input")
    text_of_resume = " "
    for page in doc:
        text_of_resume = text_of_resume + str(page.get_text())
    label_list=[]
    text_list = []
    dic = {}
    
    doc = nlp(text_of_resume)
    for ent in doc.ents:
        label_list.append(ent.label_)
        text_list.append(ent.text)
    
    print("CV Model work done")
    for i in range(len(label_list)):
        if label_list[i] in dic:
            # if the key already exists, append the new value to the list of values
            dic[label_list[i]].append(text_list[i])
        else:
            # if the key does not exist, create a new key-value pair
            dic[label_list[i]] = [text_list[i]]

    print(dic)
    resume_data_annotated = ''
    for key, value in dic.items():
        for val in value:
            resume_data_annotated += val + " "

    resume_name = dic.get('NAME')
    if resume_name is not None:
        value_name = resume_name[0]
    else:
        value_name = None

    resume_skills = dic.get('SKILLS')
    if resume_skills is not None:                  
        value_skills = resume_skills
    else:
        value_skills = None


    resume_jobpost = dic.get('JOB POST')
    if resume_jobpost is not None:
        value_jobpost = resume_jobpost
    else:
        value_jobpost = None

    resume_experience = dic.get('EXPERIENCE')
    if resume_experience is not None:
        value_experience = resume_experience
    else:
        value_experience = None

    resume_education = dic.get('EDUCATION')
    if resume_education is not None:
        value_education = resume_education
    else:
        value_education=None

    resume_certification = dic.get('CERTIFICATION')
    if resume_certification is not None:
        value_certification = resume_certification
    else:
        value_certification=None

    resume_location = dic.get('LOCATION')
    if resume_location is not None:
        value_location = resume_location
    else:
        value_location = None


    result = None
    result = resumeFetchedData.insert_one({"NAME":value_name,"JOB POST":value_jobpost,"SKILLS": value_skills,"CERTIFICATION": value_certification,"EXPERIENCE":value_experience,"EDUCATION":value_education,"LOCATION":value_location,"ResumeTitle":filename,"ResumeAnnotatedData":resume_data_annotated,"ResumeData":text_of_resume,"jd_id":jd_id})                
pass

def resume_jd_matching(user_id, job_id):
    match_percentage= Matching(user_id,job_id)
    resume_title = resumeFetchedData.find_one({"_id": ObjectId(user_id)}, {"ResumeTitle": 1})["ResumeTitle"]
    Applied_EMP.insert_one({"job_id":ObjectId(job_id),"resume_title":resume_title,"Matching_percentage":match_percentage})
pass


@job_post.route("/post_job")
def JOB_POST():
    fetched_jobs = None
    fetched_jobs = JOBS.find({},{"_id":1,"Job_Post":1,"Department":1,"CreatedAt":1,"Job_description_file_name":1,"DemandDate":1}).sort([("CreatedAt",-1)])
    if fetched_jobs == None:
        return render_template("job_post.html",errorMsg="Problem in Jobs Fetched")
    else:
        jobs={}
        cnt = 0
        for i in fetched_jobs: 
            jobs[cnt] = {"job_id":i['_id'],"Job_Post":i['Job_Post'],"Department":i['Department'],"CreatedAt":i['CreatedAt'],"Job_description_file_name":i['Job_description_file_name'],'DemandDate':i['DemandDate']}
            cnt += 1
        return render_template("job_post.html",len = len(jobs), data = jobs)


@job_post.route("/add_job", methods=["POST"])
def ADD_JOB():
    try:
        # upload JD file
        jd_file = request.files["jd"]
        if jd_file:
            # Delete all files inside the folder before saving the JD file
            for filename in os.listdir(jd_folder):
                file_path = os.path.join(jd_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            # Save the JD file to a local folder
            jd_file.save(jd_folder + jd_file.filename)
            job_post = str(request.form.get('jp'))
            department = str(request.form.get('company'))
            last_date = str(request.form.get('last_date'))
            filename = secure_filename(jd_file.filename)
            jd_id = ObjectId()
            ext = jd_file.filename.rsplit('.', 1)[1].lower()
            fetchedData = extractData(jd_folder+filename,jd_file.filename.rsplit('.',1)[1].lower())
            print("Jd Uploaded")
            result = None     
            result = JOBS.insert_one({"_id":jd_id,"Job_Post":job_post,"Job_Description":fetchedData,"Department":department,"DemandDate":last_date,"CreatedAt":datetime.now(),"Job_description_file_name":filename,})

            # with open(os.path.join(jd_folder, filename), "rb") as f:
            #     jd_data = f.read()

            # JOBS.update_one({"_id": jd_id}, {"$set": {"FileData": jd_data}})
            # print("JD added to Database")
            # Conditionally update FileData based on file type
            jd_data = None
            if ext in ["pdf", "docx"]:
                with open(os.path.join(jd_folder, filename), "rb") as f:
                    jd_data = f.read()

            if ext == "txt":
                JOBS.update_one({"_id": jd_id}, {"$set": {"FileData": fetchedData}})
            elif jd_data is not None:
                JOBS.update_one({"_id": jd_id}, {"$set": {"FileData": jd_data}})
                print("JD added to Database")
            else:
                print("Unsupported file format for FileData update")



       # Delete all files inside the folder before saving the resumes
        for filename in os.listdir(resume_folder):
            file_path = os.path.join(resume_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Upload Resumes
        resume_files = request.files.getlist("resume")
        for resume_file in resume_files:
            if resume_file:
                # Save each resume file to the local folder
                resume_file.save("static/uploaded_resumes/" + resume_file.filename)


        print("Resumes an JD Uploaded successfully.")

        # extract from resume
        for filename in os.listdir(resume_folder):
            if filename.endswith(".pdf") or filename.endswith(".docx"):
                resume_extraction(filename,jd_id)
        
        #matching
        allresumeFetchedData = resumeFetchedData.find({"jd_id": jd_id})
        for document in allresumeFetchedData:
            user_id_from_db = document.get("_id")
            print("user_id_from_db:", user_id_from_db)
            print("jd_id:",jd_id)
            resume_jd_matching(user_id_from_db,jd_id)

        
        return redirect('/HR1/post_job')
            
    except Exception as e:
        print(f"Exception Occurred: {str(e)}")


@job_post.route("/view_applied_candidates",methods=["POST","GET"])
def view_applied_candidates():
    job_id = request.form['job_id']
    result_data = None
    result_data = Applied_EMP.find({"job_id":ObjectId(job_id)},{"resume_title":1,"Matching_percentage":1}).sort([("Matching_percentage",-1)])
    if result_data == None:
        return {"StatusCode":400,"Message":"Problem in Fetching"}
    else:        
        result = {}
        cnt = 0
        result[0]=cnt
        result[1]=200
        for i in result_data:
            result[cnt+2] = {"resume_title":i['resume_title'],"Match":i['Matching_percentage']}
            cnt+=1   
        result[0]=cnt
        print("Result",result,type(result))
        return result
    

