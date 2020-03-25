from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import datetime
import shutil
from datetime import date

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="postgres://ecydmwxksovppy:855e743dd7e9e37d77dc88d9fad8f0ebb56862677bd18b01667236c0c1a54f93@ec2-54-147-209-121.compute-1.amazonaws.com:5432/dcss1m09vhtcso"
app.config['SQLALCHEMY_TRACK_MODIFICATION']=False
db=SQLAlchemy(app)
ma=Marshmallow(app)

class Album(db.Model):
    __tablename__="album"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    date=db.Column(db.String(100))
    status=db.Column(db.String(100))
    interval=db.Column(db.String(100))
    files=db.relationship('Filesdb',backref='album',lazy='dynamic')
    def __init__(self,name,date,status,interval):
        self.name=name
        self.date=date
        self.status=status
        self.interval=interval

class Filesdb(db.Model):
    __tablename__="filesdb"
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.String(100))
    filepath=db.Column(db.String(100))
    date=db.Column(db.String(100))
    status=db.Column(db.String(100))
    interval=db.Column(db.String(100))
    albumid=db.Column(db.Integer,db.ForeignKey('album.id'))

    def __init__(self,filename,filepath,date,status,interval,albumid):
        self.filename=filename
        self.filepath=filepath
        self.date=date
        self.status=status
        self.interval=interval
        self.albumid=albumid

class AlbumSchema(ma.Schema):
    class Meta:
        fields=('id','name','status','date','interval')

class FilesSchema(ma.Schema):
    class Meta:
        fields=('id','filename','filepath','date','status','interval','albumid')

album_schema=AlbumSchema()
albums_schema=AlbumSchema(many=True)

file_schema=FilesSchema()
files_schema=FilesSchema(many=True)
 
def time():
    new_date=date.today()
    new_time=datetime.datetime.now()
    current_date=new_time.strftime("%Y/%m/%d %H-%M-%S")
    return current_date
def folder_checker(args):
    new_path='D:\React\himalayafrontend\public\%s'%args
    os.chdir('D:\React\himalayafrontend\public')

    if not os.path.exists(new_path):
        os.mkdir(args)
        return({'path':new_path,'status':True})

    else:
        return({'path':new_path,'status':False})
app.config['ALLOWED_IMAGE_EXTENSION']=['JPG','JPEG','PNG']
def file_extension(args):
    new_file=None
    if "." in args:
        new_split=args.rsplit(".",2)
        new_file=new_split[1].upper()
    else:
        return False
        
    if new_file in app.config['ALLOWED_IMAGE_EXTENSION']:
        return True
    else:
        return False
def File_checker(args,kwargs):
    new_path='%s\%s'%(args,kwargs)
    print(new_path)
    os.chdir(args)
    if not os.path.exists(new_path):
        return True
    else:
        return False


# # print(time())
@app.route("/album",methods=["POST"])
def album():
    name=request.json['name']
    date=time()
    status="None"
    interval=request.json['interval']
    folder=folder_checker(name)
    if not folder['status']:
        return({'status':'Album has already been created Please provide another name'})
    
    result=Album(name,date,status,interval)
    db.session.add(result)
    db.session.commit()
    new_result=album_schema.dump(result)
    return jsonify({'data':new_result,'status':'Album sucessfully created'})
    # return album_schema.jsonify({'data':result,})
    # return({'status':'Album sucessfully created'})
    
@app.route('/getallalbum',methods=['GET'])
def getallalbum():
    result=Album.query.all()
    new_result=albums_schema.dump(result)
    return jsonify(new_result)

@app.route('/updatealbum/<id>',methods=["PUT"])
def updatealbum(id):
   
    res=request.json['status']
    interval=request.json['interval']
    
    
    album=Album.query.get(id)
    album.status=res
    album.interval=interval
    db.session.commit()
    return({'status':'updated sucessfully'})

@app.route('/deletealbum/<id>',methods=['DELETE'])
def deletealbum(id):
    result=Album.query.get(id)
   
    print(result.id)
    newpath='D:\React\himalayafrontend\public\%s'%result.name
    os.chdir('D:\React\himalayafrontend\public')
    shutil.rmtree(r'D:\React\himalayafrontend\public\%s'%result.name)
    db.session.delete(result)
    db.session.commit()
    return({'status':'deleted sucessfully'})
    



@app.route("/uploadfile",methods=['POST'])
def uploadfile():
    # album=request.headers['album']
    # filename=request.json['filename']
    albumid=None
    filepath=None
    try_filepath=None
    new_albumid=None
    # if album == "":
    #     filepath='D:\HotelHimalaya\%s'%filename
    # else:
    #     filepath='D:\HotelHimalaya\%s\%s'%(album,filename)
    # date=time()
    # albumid=None
    res=request.files.getlist('file')
    albumname=request.args.get('albumid')
    
    for i in range(len(res)):
       
            if not albumname:
                new_albumid=request.form['albumid']
            else:
                 new_albumid=albumname
            print(new_albumid)
            album=Album.query.filter_by(id=new_albumid).first()
            
            check_filepath=folder_checker(album.name)
            filepath=check_filepath['path']
            print(filepath)
            try_filepath="%s/%s"%(album.name,res[i].filename)
            print(try_filepath)
            albumid=new_albumid

            if not file_extension(res[i].filename):
                return ({'status':'the picture is invalid'})
            if not File_checker(filepath,res[i].filename):
                return ({'status':'the picture already exist with the same name'})

            filename=res[i].filename
            new_filepath='%s\%s'%(filepath,filename)
            date=time()
            interval=album.interval
            status="None"
            result=Filesdb(filename,try_filepath,date,status,interval,albumid)
            db.session.add(result)
            db.session.commit()
            res[i].save(os.path.join(filepath,res[i].filename))
            print(new_filepath)
            


    return({'status':'file uploaded sucessfully'})

@app.route("/deletefile/<id>",methods=['DELETE'])
def deletefile(id):
    result=Filesdb.query.get(id)
    new_filepath=result.filepath.replace("/",'\\')
    os.chdir('D:\React\himalayafrontend\public')
    os.remove('D:\React\himalayafrontend\public\%s'%new_filepath)
    db.session.delete(result)
    db.session.commit()
    return({'status':'deleted sucessfully'})

@app.route('/getfile/<id>',methods=['GET'])
def getfile(id):
    result=Filesdb.query.get(id)
    return file_schema.jsonify(result)

@app.route('/updatefile/<id>',methods=['PUT'])
def updatefile(id):
    album=Filesdb.query.filter_by(albumid=id).all()
    print(album)
    for i in range(len(album)):
        print(album[i].filename)
      
        
        files=Filesdb.query.get(album[i].id)
        files.status=album[i].album.status
        files.interval=album[i].album.interval
        
        db.session.commit()
    return({'status':'updated sucessfully'})
    
    

@app.route('/getallfile',methods=['GET'])
def getallfile():
    albumname=request.args.get('albumid')
    print(albumname)
    if not albumname:
        if 'display' in request.headers:
            result=Filesdb.query.filter_by(status='Approved').all()
            new_result=files_schema.dump(result)
            return jsonify(new_result)

            
        result=Filesdb.query.all()
        new_result=files_schema.dump(result)
        return jsonify(new_result)
    else:
            album=Album.query.filter_by(id=albumname).first()
            print(album.id)
            result=Filesdb.query.filter_by(albumid=album.id).all()
            new_result=files_schema.dump(result)
            return jsonify(new_result)
           


@app.route('/try',methods=['POST'])
def tryop():
    res=request.args.get('page')
    print(res)
    return({'status':'updated sucessfully'})



if __name__ == "__main__":
    app.run(debug=True)