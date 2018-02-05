from flask import Flask, request



def make_server(repository):

    web_app = Flask(__name__)

    @web_app.route('/browse/ta')
    def browse_ta():
        get_args = request.args
        category = request.args['category']
        page = request.args['page']
        hitsperpage = request.args.get('hitsperpage', type=int)

