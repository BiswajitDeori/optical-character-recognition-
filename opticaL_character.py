import cv2 as cv

from flask import Flask,render_template,request,Response

import os
import  easyocr

camer=cv.VideoCapture(0)



####################################



text1=[]

expression=[]

#######################################################

class evaluateString:

  def evalString(self,expression):
    valueStack = []
    opStack = []
    i=0

    while(i<len(expression)):
        if(expression[i] == ' '):
            continue
        if(expression[i]>='0' and expression[i] <= '9'):
            charNumber = [] #for storing number
            j = i
            while(j<len(expression) and expression[j]>='0' and expression[j] <= '9'):
                charNumber.append(expression[j])
                j += 1

            i = (j-1)
            valueStack.append(int(''.join(charNumber)))

        elif (expression[i]=='('):
            opStack.append(expression[i])

        elif (expression[i]==')'):
            while(opStack[-1]!='('):
                valueStack.append(self.applyOperation(opStack.pop(),valueStack.pop(),valueStack.pop()))
            opStack.pop()
        elif(expression[i]=='+'or expression[i]=='-'or expression[i]=='*'or expression[i]=='/'):
            while( (len(opStack)!=0) and ( self.opPrecedence(expression[i],opStack[-1]) ) ):
                valueStack.append(self.applyOperation(opStack.pop(),valueStack.pop(),valueStack.pop()))
            opStack.append(expression[i])
        i = i + 1

    while(len(opStack)!=0):
        valueStack.append(self.applyOperation(opStack.pop(),valueStack.pop(),valueStack.pop()))

    return valueStack.pop()


  def applyOperation(self,op,a,b):
    if op=='+':
        return a+b
    elif op=='-':
        return b-a
    elif op=='*':
        return a*b
    elif op=='/':
        return b/a
    else:
        return 0

  def opPrecedence(self,op1,op2):
    if (op2 == '(' or op2 == ')'):
        return False
    if ((op1 == '*' or op1 == '/') and (op2 == '+' or op2 == '-')):
        return False
    else:
        return True








#######################################################

new_datas=[]
express1=[]


reader=easyocr.Reader(['en'],gpu=True)


to_find=['0','1',"2",'3','4','5','6','7','8','9','(',')','*','%','/','+','-','x','X']


def filter(text1):
    for i in text1:
        for ww in i:
            if ww in to_find:
                if ww =='X' or ww=='x':
                    expression.append('*')
                else:
                    expression.append(ww)    
    final_value(expression)            



def final_value(expression):
    new1=""
    for i in expression:
        new1=new1+i
    express1.append(new1)    
    a = evaluateString()
    new_data=a.evalString(new1) 
    new_datas.append(new_data) 

def photo(img):
    result=reader.readtext(img)
    font=cv.FONT_HERSHEY_SIMPLEX
    for i in result:
        left = tuple([int(val) for val in i[0][0]])
        right = tuple([int(val) for val in i[0][2]])
        text=i[1]
        text1.append(text)
        img=cv.rectangle(img,left,right,(0,231,123),2)
        x,y=left
        img=cv.putText(img,text,(x,y-17),cv.FONT_HERSHEY_SIMPLEX,1,(121,11,234),2,cv.LINE_AA)
    filter(text1)
    cv.imwrite('static/after.jpg',img)   





########################################



def gen():
    while True:
       sucess,frame=camer.read()
       ret, buffer = cv.imencode('.jpg', cv.flip(frame,1))
       buffer=cv.flip(buffer,1)
       frame=buffer.tobytes()
       yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')







def capture():
    sucess,frame=camer.read()
    cv.imwrite('images_file/after.jpg',frame)
    cv.imwrite('static/file12.jpg',frame)
    



app=Flask(__name__,template_folder='temp')

@app.route('/')
def index1():
    return render_template('index1.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/tasks',methods=['POST','GET'])
def tasks():
   if request.method=='POST':
       if request.form.get('click')=='Capture':
           capture()
           img=cv.imread('images_file/after.jpg')
           text1.clear()
           express1.clear()
           expression.clear()
           new_datas.clear()
           photo(img)
           return render_template('after.html',data=express1[0],final=new_datas[0])
       if request.form.get('click')=='Import':
           camer.release()
           cv.destroyAllWindows()
           return render_template('index.html')  





@app.route('/after',methods=["GET","POST"])
def after():
    img=request.files['file']
    
    img.save('static/file12.jpg')
    img1=cv.imread('static/file12.jpg')
    text1.clear()
    express1.clear()
    expression.clear()
    new_datas.clear()
    photo(img1)

    
    return render_template('after.html',data=express1[0],final=new_datas[0])




if __name__=="__main__":
    app.run(port=3000,debug=True)