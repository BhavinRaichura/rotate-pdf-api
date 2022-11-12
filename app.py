from flask import Flask, render_template,request,jsonify, send_file
from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import datetime
import io

app = Flask(__name__)

app.config['INPUT_FOLDER'] = "/home/bhavin/Desktop/Rotate_PDF/pdf/input/"
app.config['OUTPUT_FOLDER'] = "/home/bhavin/Desktop/Rotate_PDF/pdf/output/"

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/pdf/rotate',methods =['GET','POST'])
def rotate_pdf():
    
    def rotate_pdf(file_name, rotate_page, angle):
        tarfile = app.config['INPUT_FOLDER']+file_name
        outfile = open(app.config['OUTPUT_FOLDER']+file_name,'wb')
        pdf =  PdfFileReader(tarfile)
        writer = PdfFileWriter()
        len_pdf = pdf.getNumPages()
        if rotate_page > len_pdf or rotate_page<=0:
            return False
        for i in range(len_pdf):
            page = pdf.getPage(i)
            if(rotate_page-1==i):
                page.rotate(angle)
            writer.addPage(page)
        writer.write(outfile)
        outfile.close()
        return True
    
    msg = "Invalid Request"
        
    if request.method == "POST":
        angle_of_rotation = int(request.form['angle_of_rotation'])
        page_number = int(request.form['page_number'])
        file= request.files['file']
        
        if(angle_of_rotation%90!=0):
            msg = "Invalid Angle"
            
        elif len(file.filename)>4 and file.filename[-4:] == ".pdf":
            # save input file with new unique name
            file_name = "rotate_" + str(datetime.datetime.today()) + ".pdf"
            file.save(app.config['INPUT_FOLDER'] + file_name)
            # function call to rotate pfd
            flag = rotate_pdf(file_name, page_number, angle_of_rotation)
            # check if pdf get successfully rotated or not
            if flag == False:
                os.remove(app.config['INPUT_FOLDER'] + file_name)
                os.remove(app.config['OUTPUT_FOLDER'] + file_name)
                res = jsonify({"msg":"Page number is out of range"})
                res.status_code = 400
                return res
            # convert output retated pdf into bytes
            output_file = io.BytesIO()
            with open(app.config['OUTPUT_FOLDER'] + file_name, 'rb') as fo:
                output_file.write(fo.read())
            output_file.seek(0)
            # remove files saved in system
            os.remove(app.config['INPUT_FOLDER'] + file_name)
            os.remove(app.config['OUTPUT_FOLDER'] + file_name)
            # send file
            return send_file(output_file, mimetype='application/pdf', download_name= 'output.pdf')
        
        else:
            msg="File type is not valid. Please send PDF file"
            
    res = jsonify({"message":msg})
    res.status_code = 400
    return res
        

if __name__ == "__main__":
    app.run(debug = True)