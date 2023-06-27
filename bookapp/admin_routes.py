import re,random,os
from flask import render_template, request, redirect, flash,make_response,session,url_for
from sqlalchemy.sql import text
from bookapp import app, csrf
from bookapp.models import db,Admin,Book,Category




@app.route("/admin/login", methods=['GET','POST'])
def adminlogin():
    if request.method=='GET':
        return render_template("admin/login.html")
    else:
        username=request.form.get('username')
        pwd=request.form.get('password')
        chk=db.session.query(Admin).filter(Admin.admin_username==username, Admin.admin_pwd==pwd).count()
        if chk:
            session['admin_loggedin']=True
            return redirect('/admin/dashboard')
        else:
            flash('incorrect credntials')
            return redirect('/admin/login')

@app.route("/admin/logout")
def admin_logout():
    if session.get('admin_loggedin'):
        session.pop('admin_loggedin',None)
        flash('you have logged out successfully')
    return render_template("admin/admin_dashboard.html")



@app.route("/admin/dashboard")
def adminhome():
    return render_template("admin/admin_dashboard.html")



@app.route("/admin/newbook", methods=['POST','GET'])
def add_newbook():
    if session.get('admin_loggedin')== None:
        flash ('Access Denied' ,category='danger')
        return redirect('/admin/login')

    if request.method=='GET':
        cats=db.session.query(Category).all()
        return render_template("admin/addbook.html", cats=cats)
    else:
        bookcat=request.form.get('bookcat')
        year=request.form.get('title')
        title=request.form.get('year')
        status=request.form.get('status')
        cover=request.files.get('cover')
        desc=request.form.get('desc')
        if title!=''and cover:
            filename=cover.filename
            allowed=['.jpg','png','.jpeg']
            name,ext=os.path.splitext(filename)
            newname= str (random.random()*10000)+ext
            if ext.lower() in allowed:
                cover.save('bookapp/static/collections/'+newname)
                b = Book(book_title=title,book_desc=desc,book_cover=newname,book_publication=year,book_catid=bookcat,book_status=status)
                db.session.add(b)
                db.session.commit()
                flash('Book has been added' ,category='success')
                return redirect('/admin/books')
            else:
                flash('Plese upload only type jpg,png or jpeg',category='danger')
                return redirect("admin/newbook")
        else:
            flash('please ensure you complete the required question',category='danger')
            return redirect('/admin/newbook')


@app.route("/admin/books")
def manage_book():
    books=db.session.query(Book).all()
    return render_template("admin/allbooks.html",books=books)


@app.route("/admin/deletebook/<id>")
def delete_book(id):
    if session.get('admin_loggedin') == None:
        flash('Acces denied')
        return redirect('/admin/login')
    else:
        bk=db.session.query(Book).get_or_404(id)
        os.remove("bookapp/static/collections/"+bk.book_cover)
        db.session.delete(bk)
        db.session.commit()
        flash(f'Book {bk.book_title} has been deleted!',category='success')
        return redirect('/admin/books')
    