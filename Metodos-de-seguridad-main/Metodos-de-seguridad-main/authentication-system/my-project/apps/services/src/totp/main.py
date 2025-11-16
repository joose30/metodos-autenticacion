from adapters.http.flask_controller import app

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
