from flask import Flask, request, render_template, session, url_for
import logging
import math

from repositories.MongoRepository import MongoRepository


def make_web_app(repository):
    web_app = Flask(__name__)

    @web_app.route('/')
    def show_citations():
        query = request.args.get('q') or None
        current_page = int(request.args.get('page', 1))
        hits_per_page = int(request.args.get('hitsperpage', 100))
        skip = (current_page - 1) * hits_per_page
        result = repository.find_citations(query=query, limit=hits_per_page, skip=skip)
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
            'previous': url_for('show_citations', query=query, hitsperpage=hits_per_page,
                                page=current_page - 1) if skip > 0 else None,
            'next': url_for('show_citations', query=query, hitsperpage=hits_per_page,
                            page=current_page + 1) if skip + 1 + len(citations) < total else None,
            'total': total,
            'pages': [{
                'number': page_num,
                'url': url_for('show_citations', query=query, hitsperpage=hits_per_page,
                               page=page_num) if page_num != current_page else None
            } for page_num in range(page_window[0], page_window[1] +1)]
        }

        return render_template(
            'citation_list.html',
            citations=citations,
            pagination=pagination,
            groups={},
        )

    @web_app.route('/entries/<volume>/<int:number>')
    def show_entry(volume, number):
        if volume.isdigit():
            volume = int(volume)
        citation = repository.get_citation(volume=volume, number=number)
        return render_template(
            'citation.html',
            citation=citation
        )

    web_app.secret_key = '$%#$%wdsfej/3yX $%#$%R~dsfewmN]LWX/,fgfa?'
    return web_app


if __name__ == '__main__':
    repository = MongoRepository('ta')
    web_app = make_web_app(repository)
    web_app.run('0.0.0.0', debug=True)
