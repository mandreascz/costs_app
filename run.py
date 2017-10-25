from flask import Flask, request
import app as ocr_app
import json

app = Flask(__name__)

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(f.filename)

      text = ocr_app.ocr.extract_text_from_image(f.filename)
      obj = ocr_app.ParserFactory.find_receipt_type(text)
      d = obj.parse()
      dd = dict()
      dd['data'] = d['data'].to_dict('records')
      dd['total'] = d['total']
      response = app.response_class(
          response=json.dumps(dd),
          status=200,
          mimetype='application/json'
      )
      return response

if __name__ == '__main__':
    app.run(debug=True)