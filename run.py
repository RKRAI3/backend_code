from app import create_app


if __name__ == '__main__':
    app = create_app()
    # app.run(ssl_context=('/home/ubuntu/cert.pem','/home/ubuntu/key.pem'),host='0.0.0.0',port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
