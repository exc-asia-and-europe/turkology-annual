import argparse
from flask import Flask, request, render_template, session, url_for
import logging
import math
import os
import pprint
from werkzeug.urls import url_encode

from repositories.MongoRepository import MongoRepository


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--port', '-p', type=int, default=5000, help='Port to listen on')
    args = parser.parse_args()

    repository = MongoRepository('ta')
    web_app = make_web_app(repository)
    debug = os.environ.get('ENV') != 'PROD'
    web_app.run('0.0.0.0', debug=debug, port=args.port)


def make_web_app(repository):
    web_app = Flask(__name__)

    @web_app.route('/')
    def show_citations():
        query = request.args.get('q') or None
        current_page = int(request.args.get('page', 1))
        hits_per_page = int(request.args.get('hitsperpage', 100))
        skip = (current_page - 1) * hits_per_page
        fullyParsed = {'1': True, '0': False}.get(request.args.get('fullyParsed'))
        result = repository.find_citations(query=query, limit=hits_per_page, skip=skip, fullyParsed=fullyParsed)
        citations = result['data']
        total = result['total']

        total_page_count = math.ceil(total / hits_per_page)
        page_window = [current_page - 10, current_page + 10]
        if page_window[0] < 1:
            difference = 1 - page_window[0]
            page_window = [1, page_window[1] + difference]
        if page_window[1] > total_page_count:
            page_window[1] = total_page_count

        pagination = {
            'start_index': skip + 1,
            'previous': modify_query(page=current_page - 1) if skip > 0 else None,
            'next': modify_query(page=current_page + 1) if skip + 1 + len(citations) < total else None,
            'total': total,
            'pages': [{
                'number': page_num,
                'url': modify_query(page=page_num) if page_num != current_page else None
            } for page_num in range(page_window[0], page_window[1] + 1)]
        }

        return render_template(
            'citation_list.html',
            citations=citations,
            pagination=pagination,
            number_of_matches=total,
            groups={},
            fullyParsed=fullyParsed,
        )

    @web_app.route('/entries/<volume>/<int:number>')
    def show_entry(volume, number):
        version = request.args.get('version')
        if volume.isdigit():
            volume = int(volume)
        citation = repository.get_citation(volume=volume, number=number, version=version)
        citation_pretty = dict([(key, value) for key, value in citation.items() if not key.startswith('_')])
        return render_template(
            'citation.html',
            citation=citation,
            citation_pretty=pprint.pformat(citation_pretty, indent=4, width=80)
        )

    @web_app.template_global()
    def modify_query(**new_values):
        args = request.args.copy()

        for key, value in new_values.items():
            args[key] = value

        return '{}?{}'.format(request.path, url_encode(args))

    web_app.secret_key = '$%#$%wdsfej/3yX $%#$%R~dsfewmN]LWX/,fgfa?'
    return web_app


if __name__ == '__main__':
    main()
