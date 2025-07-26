from app import create_app


if __name__ == '__main__':
    app = create_app()
    print("Starting the application...")
    app.run(debug=False)
    # app.run(debug=True, host='0.0.0.0', port=5000)