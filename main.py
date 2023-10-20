from flask import Flask,render_template,redirect,request
app=Flask(__name__)


@app.route("/")
def start():

    return render_template("home.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        name=request.form.get("name")
        password=request.form.get("password")
        if name =="mohamed" and password=="1234":
            return render_template("secret.html")
        else:
            return redirect("/")


    return render_template("login.html")
@app.route("/register")
def register():
    user=input("please provide me with the  username\n")
    password=input("please give me the password \n")

    return redirect("/mohamed")

if __name__=="__main__":
    app.run(debug=True)



