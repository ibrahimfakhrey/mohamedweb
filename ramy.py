from flask import Flask,render_template
app=Flask(__name__)
@app.route("/")
def start():
    names=[]
    for i in range(4):
        x=input("whats your name")
    names .append(x)
    render_template("index.html",name=names)
if __name__=="__main__":
    app.run(debug=True)