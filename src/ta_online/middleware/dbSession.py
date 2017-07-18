from ta_online.settings import Session


class SqlaMiddleware():
    def process_request(self, request):
        request.db_session = Session()


    def process_response(self, request, response):
        try:
            request.db_session.close()
        # request.db_session.commit()

        except AttributeError:
            pass
        return response
