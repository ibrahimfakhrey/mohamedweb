from flask import Flask, render_template, request

app=Flask(__name__)

@app.route("/",methods=["GET","POST"])
def start ():
    name=None
    if request.method=="POST":
        name=request.form.get("name")
        return render_template("index.html", name=name)

    return   render_template("index.html",name=name)

@app.route("/ramy",methods=["GET","POST"])
def ramy():
    if request.method=="POST":
        name=request.form.get("name")
        return f"welcome {name}"
    return render_template("ramy.html")


if __name__=="__main__":
    app.run(debug=True)