from flask import Flask, render_template,redirect
from database import mongo
import os
  
app = Flask(__name__)
app.secret_key = "Resume_screening"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.config['MONGO_URI']= 'mongodb://localhost:27017/resumerankingtest'


mongo.init_app(app)
resumeFetchedData = mongo.db.resumeFetchedData
Applied_EMP=mongo.db.Applied_EMP
IRS_USERS = mongo.db.IRS_USERS
JOBS = mongo.db.JOBS
resume_uploaded = False
from Job_post import job_post
app.register_blueprint(job_post,url_prefix="/HR1")



@app.route('/')
def index():
    # return render_template("job_post.html")  
    return redirect('/HR1/post_job')     

if __name__=="__main__":
    app.run(debug=True)